import json
import re
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool

from app.agents.action_logger import log_agent_action
from app.core.sanitization import sanitize_mapping, sanitize_text
from app.integrations.fbr_ecosystem import send_callback_to_fbr_dev, send_callback_to_fbr_suporte
from app.integrations.schemas import FbrEcosystemCallback
from app.webhooks.schemas import FbrDevEventPayload, FbrSuporteLeadPayload, GenericWebhookAck, LeadHandoffPayload, LeadHandoffResult

DEFAULT_SPACE_ID = UUID("20000000-0000-0000-0000-000000000001")
DEFAULT_AGENT_ID = UUID("40000000-0000-0000-0000-000000000001")
DEFAULT_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DEV_CHANNEL_ID = UUID("30000000-0000-0000-0000-000000000002")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "deal"


async def process_fbr_leads_handoff(pool: Pool, payload: LeadHandoffPayload) -> LeadHandoffResult:
    workspace_id = UUID(payload.workspace_id)
    seller_user_id = DEFAULT_USER_ID

    async with pool.acquire() as connection:
        async with connection.transaction():
            existing_intake = await connection.fetchrow(
                "SELECT id FROM lead_intakes WHERE workspace_id = $1 AND source_system = $2 AND external_reference = $3 ORDER BY created_at DESC LIMIT 1",
                workspace_id,
                payload.source_system,
                payload.external_reference,
            )
            if existing_intake is not None:
                existing_deal = await connection.fetchrow(
                    "SELECT id, channel_id FROM deals WHERE workspace_id = $1 AND lead_intake_id = $2 ORDER BY created_at DESC LIMIT 1",
                    workspace_id,
                    existing_intake['id'],
                )
                existing_task = None
                if existing_deal is not None:
                    existing_task = await connection.fetchrow(
                        "SELECT id FROM tasks WHERE workspace_id = $1 AND deal_id = $2 ORDER BY created_at DESC LIMIT 1",
                        workspace_id,
                        existing_deal['id'],
                    )
                return LeadHandoffResult(
                    intake_id=str(existing_intake['id']),
                    deal_id=str(existing_deal['id']) if existing_deal else '',
                    channel_id=str(existing_deal['channel_id']) if existing_deal and existing_deal['channel_id'] else '',
                    task_id=str(existing_task['id']) if existing_task else '',
                    status='accepted',
                )

            lead_name = sanitize_text(payload.lead_name) or payload.lead_name
            company_name = sanitize_text(payload.company_name)
            notes = sanitize_text(payload.notes)
            temperature = sanitize_text(payload.temperature) or payload.temperature
            origin = sanitize_text(payload.origin) or payload.origin
            virtual_manager_slug = sanitize_text(payload.virtual_manager_slug) or payload.virtual_manager_slug
            metadata = sanitize_mapping(payload.metadata)
            handoff_payload = sanitize_mapping(payload.handoff_payload)

            intake_metadata = {
                **metadata,
                'origin': origin,
                'whatsapp': sanitize_text(payload.whatsapp),
                'virtual_manager_slug': virtual_manager_slug,
            }
            intake = await connection.fetchrow(
                "INSERT INTO lead_intakes (workspace_id, source_type, source_system, external_reference, lead_name, company_name, email, phone, score, temperature, metadata, handoff_payload) VALUES ($1, 'fbr_leads', $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11::jsonb) RETURNING id",
                workspace_id,
                payload.source_system,
                payload.external_reference,
                lead_name,
                company_name,
                sanitize_text(payload.email),
                sanitize_text(payload.whatsapp) or sanitize_text(payload.phone),
                payload.score,
                temperature,
                json.dumps(intake_metadata),
                json.dumps(handoff_payload),
            )
            company_label = company_name or lead_name
            channel_slug = f"{_slugify(company_label)}-{_slugify(payload.external_reference)}"
            channel = await connection.fetchrow(
                "INSERT INTO channels (workspace_id, space_id, slug, name, channel_type) VALUES ($1, $2, $3, $4, 'deal') RETURNING id",
                workspace_id,
                DEFAULT_SPACE_ID,
                f"deal-{channel_slug}",
                company_label,
            )
            deal = await connection.fetchrow(
                "INSERT INTO deals (workspace_id, lead_intake_id, channel_id, assignee_user_id, company_name, contact_name, contact_email, stage, origin_badge, score) VALUES ($1, $2, $3, $4, $5, $6, $7, 'qualification', 'fbr-leads', $8) RETURNING id",
                workspace_id,
                intake['id'],
                channel['id'],
                seller_user_id,
                company_label,
                lead_name,
                sanitize_text(payload.email),
                payload.score,
            )
            task = await connection.fetchrow(
                "INSERT INTO tasks (workspace_id, deal_id, channel_id, assignee_user_id, title, description, priority, source) VALUES ($1, $2, $3, $4, $5, $6, 'high', 'agent') RETURNING id",
                workspace_id,
                deal['id'],
                channel['id'],
                seller_user_id,
                'Fazer primeiro contato com lead aquecido',
                notes or 'Lead aquecido recebido do 1FBR-Leads.',
            )
            await connection.execute(
                "INSERT INTO messages (workspace_id, channel_id, author_type, author_id, body, source_system) VALUES ($1, $2, 'agent', $3, $4, '1FBR-Leads')",
                workspace_id,
                channel['id'],
                str(DEFAULT_AGENT_ID),
                f"Lead aquecido recebido do 1FBR-Leads: {lead_name}.",
            )

        await log_agent_action(
            pool=pool,
            workspace_id=workspace_id,
            agent_id=DEFAULT_AGENT_ID,
            action_type='lead_handoff_intake',
            trigger_type='webhook',
            payload=payload.model_dump(mode='json'),
            result={'intake_id': str(intake['id']), 'deal_id': str(deal['id']), 'channel_id': str(channel['id']), 'task_id': str(task['id'])},
        )

    return LeadHandoffResult(intake_id=str(intake['id']), deal_id=str(deal['id']), channel_id=str(channel['id']), task_id=str(task['id']), status='accepted')


async def process_fbr_dev_event(pool: Pool, payload: FbrDevEventPayload) -> GenericWebhookAck:
    workspace_id = UUID(payload.workspace_id)
    title = sanitize_text(payload.title) or payload.title
    description = sanitize_text(payload.description) or ''
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "INSERT INTO messages (workspace_id, channel_id, author_type, author_id, body, source_system) VALUES ($1, $2, 'agent', $3, $4, '1FBR-Dev') RETURNING id",
            workspace_id,
            DEV_CHANNEL_ID,
            str(DEFAULT_AGENT_ID),
            f"[{payload.event_type}] {title}: {description}",
        )

    callback_event = FbrEcosystemCallback(
        workspace_id=payload.workspace_id,
        source_system='FBR-CLICK',
        event_type='dev_event_received',
        status='accepted',
        reference_id=payload.external_reference,
        related_entity_id=str(row['id']),
        occurred_at=datetime.now(timezone.utc),
    )
    delivery = await send_callback_to_fbr_dev(callback_event)

    await log_agent_action(
        pool=pool,
        workspace_id=workspace_id,
        agent_id=DEFAULT_AGENT_ID,
        action_type='fbr_dev_event',
        trigger_type='webhook',
        payload=payload.model_dump(mode='json'),
        result={'message_id': str(row['id']), 'delivery': delivery},
    )
    return GenericWebhookAck(status='accepted', reference_id=str(row['id']))


async def process_fbr_suporte_handoff(pool: Pool, payload: FbrSuporteLeadPayload) -> GenericWebhookAck:
    workspace_id = UUID(payload.workspace_id)
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "INSERT INTO lead_intakes (workspace_id, source_type, source_system, external_reference, lead_name, company_name, email, phone, metadata, handoff_payload) VALUES ($1, 'support', $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb) RETURNING id",
            workspace_id,
            payload.source_system,
            payload.external_reference,
            sanitize_text(payload.lead_name) or payload.lead_name,
            sanitize_text(payload.company_name),
            sanitize_text(payload.email),
            sanitize_text(payload.phone),
            json.dumps(sanitize_mapping(payload.metadata)),
            json.dumps(sanitize_mapping(payload.model_dump(mode='json'))),
        )

    callback_event = FbrEcosystemCallback(
        workspace_id=payload.workspace_id,
        source_system='FBR-CLICK',
        event_type='support_handoff_received',
        status='accepted',
        reference_id=payload.external_reference,
        related_entity_id=str(row['id']),
        occurred_at=datetime.now(timezone.utc),
    )
    delivery = await send_callback_to_fbr_suporte(callback_event)

    await log_agent_action(
        pool=pool,
        workspace_id=workspace_id,
        agent_id=DEFAULT_AGENT_ID,
        action_type='fbr_suporte_handoff',
        trigger_type='webhook',
        payload=payload.model_dump(mode='json'),
        result={'intake_id': str(row['id']), 'delivery': delivery},
    )
    return GenericWebhookAck(status='accepted', reference_id=str(row['id']))
