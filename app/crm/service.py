import json
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool

from app.agents.action_logger import log_platform_action
from app.agents.websocket import workspace_manager
from app.crm.schemas import DealFeedbackOut, DealFeedbackUpdate, DealListOut, DealOut, DealStageEventOut, DealStageMetaOut, DealStageUpdate
from app.integrations.fbr_leads import send_stage_event_to_fbr_leads
from app.messaging.websocket import manager

CANONICAL_STAGES = [
    'first_contact',
    'qualification',
    'proposal',
    'negotiation',
    'follow_up',
    'reengagement',
    'closed_won',
    'closed_lost',
    'cancelled',
]

STAGE_TRANSITIONS = {
    'first_contact': ['qualification', 'follow_up', 'closed_lost'],
    'qualification': ['proposal', 'follow_up', 'closed_lost'],
    'proposal': ['negotiation', 'follow_up', 'closed_won', 'closed_lost'],
    'negotiation': ['closed_won', 'follow_up', 'closed_lost'],
    'follow_up': ['qualification', 'proposal', 'negotiation', 'reengagement', 'closed_lost'],
    'reengagement': ['first_contact', 'qualification', 'closed_lost'],
    'closed_won': [],
    'closed_lost': [],
    'cancelled': [],
}

LOSS_REASONS = [
    'sem_resposta',
    'sem_budget',
    'sem_fit',
    'concorrente',
    'momento_errado',
    'contato_invalido',
    'nao_quis_avancar',
    'duplicado',
]

WIN_REASONS = [
    'fechamento_comercial',
    'upgrade',
    'renovacao',
    'reativacao',
    'fit_confirmado',
]

STAGE_ALIASES = {
    'prospecting': 'first_contact',
    'primeiro contato': 'first_contact',
    'primeiro_contato': 'first_contact',
    'first_contact': 'first_contact',
    'qualificacao': 'qualification',
    'qualification': 'qualification',
    'proposta': 'proposal',
    'proposal': 'proposal',
    'negociacao': 'negotiation',
    'negotiation': 'negotiation',
    'follow-up': 'follow_up',
    'follow_up': 'follow_up',
    'reengajamento': 'reengagement',
    'reengagement': 'reengagement',
    'ganho': 'closed_won',
    'won': 'closed_won',
    'closed_won': 'closed_won',
    'perdido': 'closed_lost',
    'lost': 'closed_lost',
    'closed_lost': 'closed_lost',
    'cancelado': 'cancelled',
    'cancelled': 'cancelled',
}


def list_stage_meta() -> DealStageMetaOut:
    return DealStageMetaOut(
        stages=CANONICAL_STAGES,
        transitions=STAGE_TRANSITIONS,
        loss_reasons=LOSS_REASONS,
        win_reasons=WIN_REASONS,
    )


def normalize_stage(value: str) -> str:
    normalized = value.strip().lower().replace('-', '_')
    if normalized not in STAGE_ALIASES:
        raise ValueError(f'Unknown stage: {value}.')
    return STAGE_ALIASES[normalized]


def _resolve_outcome(stage: str) -> str | None:
    if stage == 'closed_won':
        return 'won'
    if stage == 'closed_lost':
        return 'lost'
    return None


def _validate_reason(stage: str, reason_code: str | None) -> None:
    if stage == 'closed_lost':
        if not reason_code:
            raise ValueError('reason_code is required for closed_lost.')
        if reason_code not in LOSS_REASONS:
            raise ValueError(f'Invalid loss reason: {reason_code}.')
    if stage == 'closed_won':
        if not reason_code:
            raise ValueError('reason_code is required for closed_won.')
        if reason_code not in WIN_REASONS:
            raise ValueError(f'Invalid win reason: {reason_code}.')


def _build_upstream_event(
    *,
    row: object,
    previous_stage: str | None,
    current_stage: str,
    changed_by_type: str,
    reason_code: str | None,
    reason_notes: str | None,
    changed_at: datetime,
) -> DealStageEventOut:
    data = dict(row)
    return DealStageEventOut(
        external_reference=data.get('external_reference'),
        deal_id=str(data['id']),
        event_type='deal_closed' if current_stage in {'closed_won', 'closed_lost'} else 'deal_stage_changed',
        stage=current_stage,
        previous_stage=previous_stage,
        outcome=_resolve_outcome(current_stage),
        reason_code=reason_code,
        reason_notes=reason_notes,
        changed_at=changed_at.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
        changed_by_type=changed_by_type,
        upstream_system=data.get('source_system') or 'unknown',
    )


async def list_deals(pool: Pool, workspace_id: UUID) -> DealListOut:
    rows = await pool.fetch(
        'SELECT id, company_name, contact_name, contact_email, stage, origin_badge, score FROM deals WHERE workspace_id = $1 ORDER BY created_at DESC',
        workspace_id,
    )
    deals = []
    for row in rows:
        data = dict(row)
        data['stage'] = normalize_stage(str(data['stage']))
        deals.append(DealOut(**data))
    return DealListOut(deals=deals)


async def execute_stage_transition(
    pool: Pool,
    workspace_id: UUID,
    deal_id: UUID,
    *,
    stage: str,
    reason_code: str | None = None,
    reason_notes: str | None = None,
    changed_by_type: str = 'human',
) -> dict[str, object]:
    target_stage = normalize_stage(stage)
    _validate_reason(target_stage, reason_code)

    async def _run(connection: object) -> tuple[object, object | None, str, datetime, UUID | None]:
        current = await connection.fetchrow(
            'SELECT id, stage, lead_intake_id FROM deals WHERE id = $1 AND workspace_id = $2',
            deal_id,
            workspace_id,
        )
        if current is None:
            raise ValueError('Deal not found.')

        current_stage = normalize_stage(str(current['stage']))
        if current_stage != target_stage and target_stage not in STAGE_TRANSITIONS[current_stage]:
            raise ValueError(f'Invalid stage transition from {current_stage} to {target_stage}.')

        metadata = {
            'reason_code': reason_code,
            'reason_notes': reason_notes,
        }
        status = _resolve_outcome(target_stage) or ('cancelled' if target_stage == 'cancelled' else 'open')
        row = await connection.fetchrow(
            """
            UPDATE deals
            SET stage = $1, status = $2
            WHERE id = $3 AND workspace_id = $4
            RETURNING id, lead_intake_id, channel_id, company_name, contact_name, contact_email, stage, origin_badge, score
            """,
            target_stage,
            status,
            deal_id,
            workspace_id,
        )
        changed_at = datetime.now(timezone.utc)
        await connection.execute(
            'INSERT INTO deal_history (workspace_id, deal_id, from_stage, to_stage, changed_by_type, metadata) VALUES ($1, $2, $3, $4, $5, $6::jsonb)',
            workspace_id,
            deal_id,
            current_stage,
            target_stage,
            changed_by_type,
            json.dumps(metadata),
        )
        intake = None
        if row['lead_intake_id']:
            intake = await connection.fetchrow(
                'SELECT external_reference, source_system FROM lead_intakes WHERE id = $1 AND workspace_id = $2',
                row['lead_intake_id'],
                workspace_id,
            )
        return row, intake, current_stage, changed_at, row['channel_id']

    if hasattr(pool, 'acquire'):
        async with pool.acquire() as connection:
            async with connection.transaction():
                row, intake, current_stage, changed_at, channel_id = await _run(connection)
    else:
        row, intake, current_stage, changed_at, channel_id = await _run(pool)

    result_data = dict(row)
    result_data['stage'] = target_stage
    deal = DealOut(**result_data)
    event_row = {
        'id': row['id'],
        'external_reference': intake['external_reference'] if intake else None,
        'source_system': intake['source_system'] if intake else 'unknown',
    }
    upstream_event = _build_upstream_event(
        row=event_row,
        previous_stage=current_stage,
        current_stage=target_stage,
        changed_by_type=changed_by_type,
        reason_code=reason_code,
        reason_notes=reason_notes,
        changed_at=changed_at,
    )
    delivery = await send_stage_event_to_fbr_leads(upstream_event)
    stage_payload = {'deal_id': str(deal.id), 'stage': deal.stage}
    if channel_id is not None:
        await manager.broadcast(str(channel_id), 'deal_stage_changed', stage_payload)
    await workspace_manager.broadcast(str(workspace_id), 'deal_stage_changed', stage_payload)
    return {
        'deal': deal,
        'previous_stage': current_stage,
        'upstream_event': upstream_event,
        'delivery': delivery,
    }


async def update_deal_stage(pool: Pool, workspace_id: UUID, deal_id: UUID, payload: DealStageUpdate) -> DealOut:
    result = await execute_stage_transition(
        pool,
        workspace_id,
        deal_id,
        stage=payload.stage,
        reason_code=payload.reason_code,
        reason_notes=payload.reason_notes,
        changed_by_type='human',
    )
    deal = result['deal']
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='deal_stage_changed',
        trigger_type='api',
        payload={'deal_id': str(deal_id), **payload.model_dump(mode='json')},
        result={
            'deal_id': str(deal.id),
            'stage': deal.stage,
            'upstream_event': result['upstream_event'].model_dump(mode='json'),
            'delivery': result['delivery'],
        },
    )
    return deal


async def create_upstream_feedback(pool: Pool, workspace_id: UUID, deal_id: UUID, payload: DealFeedbackUpdate) -> DealFeedbackOut:
    terminal_stage = 'closed_won' if payload.outcome == 'won' else 'closed_lost'
    _validate_reason(terminal_stage, payload.reason_code)

    async with pool.acquire() as connection:
        async with connection.transaction():
            current = await connection.fetchrow(
                'SELECT stage, channel_id FROM deals WHERE id = $1 AND workspace_id = $2',
                deal_id,
                workspace_id,
            )
            if current is None:
                raise ValueError('Deal not found.')
            previous_stage = normalize_stage(str(current['stage']))
            row = await connection.fetchrow(
                """
                UPDATE deals
                SET stage = $1, status = $2
                WHERE id = $3 AND workspace_id = $4
                RETURNING id, lead_intake_id, channel_id, company_name, contact_name, contact_email, origin_badge
                """,
                terminal_stage,
                payload.outcome,
                deal_id,
                workspace_id,
            )
            changed_at = datetime.now(timezone.utc)
            await connection.execute(
                'INSERT INTO deal_history (workspace_id, deal_id, from_stage, to_stage, changed_by_type, metadata) VALUES ($1, $2, $3, $4, $5, $6::jsonb)',
                workspace_id,
                deal_id,
                previous_stage,
                terminal_stage,
                'human',
                json.dumps({'reason_code': payload.reason_code, 'reason_notes': payload.reason_notes, 'outcome': payload.outcome}),
            )
            intake = None
            if row['lead_intake_id']:
                intake = await connection.fetchrow(
                    'SELECT external_reference, source_system FROM lead_intakes WHERE id = $1 AND workspace_id = $2',
                    row['lead_intake_id'],
                    workspace_id,
                )

    event_row = {
        'id': row['id'],
        'external_reference': intake['external_reference'] if intake else None,
        'source_system': intake['source_system'] if intake else 'unknown',
    }
    upstream_event = _build_upstream_event(
        row=event_row,
        previous_stage=previous_stage,
        current_stage=terminal_stage,
        changed_by_type='human',
        reason_code=payload.reason_code,
        reason_notes=payload.reason_notes,
        changed_at=changed_at,
    )
    delivery = await send_stage_event_to_fbr_leads(upstream_event)
    stage_payload = {'deal_id': str(row['id']), 'stage': terminal_stage}
    if row['channel_id'] is not None:
        await manager.broadcast(str(row['channel_id']), 'deal_stage_changed', stage_payload)
    await workspace_manager.broadcast(str(workspace_id), 'deal_stage_changed', stage_payload)
    result = DealFeedbackOut(
        deal_id=str(row['id']),
        outcome=payload.outcome,
        reason_code=payload.reason_code,
        reason_notes=payload.reason_notes,
        upstream_system=str(intake['source_system']) if intake else 'unknown',
        upstream_payload=upstream_event.model_dump(mode='json'),
        delivery=delivery,
    )
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='deal_feedback_created',
        trigger_type='api',
        payload={'deal_id': str(deal_id), **payload.model_dump(mode='json')},
        result=result.model_dump(mode='json'),
    )
    return result
