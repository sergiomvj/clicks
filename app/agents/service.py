import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from asyncpg import Pool

from app.agents.action_logger import log_agent_action, log_platform_action
from app.agents.schemas import (
    AgentControlOut,
    AgentControlUpdateRequest,
    AgentExecutionOut,
    AgentListOut,
    AgentMarkdownCacheListOut,
    AgentMarkdownCacheOut,
    AgentOut,
    AgentRegistrationOut,
    AgentRegistrationRequest,
    AgentHeartbeatOut,
    AgentTokenOut,
    AgentTokenRequest,
    AgentValidationOut,
    ApprovalCreateRequest,
    ApprovalDecisionRequest,
    ApprovalListOut,
    ApprovalOut,
    AuditLogListOut,
    AuditLogOut,
)
from app.agents.websocket import workspace_manager
from app.core.redis import get_redis_client
from app.core.sanitization import sanitize_text
from app.core.security import build_agent_token_cache_key, create_agent_access_token
from app.crm.service import CANONICAL_STAGES, execute_stage_transition, normalize_stage
from app.messaging.websocket import manager

REQUIRED_AGENT_FILES = [
    'SOUL.md',
    'IDENTITY.md',
    'TASKS.md',
    'AGENTS.md',
    'MEMORY.md',
    'TOOLS.md',
    'USER.md',
]

AGENT_POLICIES = {
    'comercial-bot': {
        'scope_actions': ['review_lead', 'draft_message', 'suggest_stage_change', 'create_follow_up_task'],
        'approval_required_actions': ['send_message', 'change_deal_stage', 'edit_lead_data', 'trigger_external_webhook'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
    'report-bot': {
        'scope_actions': ['summarize_pipeline', 'report_sla', 'report_conversion', 'report_loss_reasons'],
        'approval_required_actions': ['trigger_external_webhook'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
    'onboarding-bot': {
        'scope_actions': ['review_new_lead', 'prepare_onboarding_checklist', 'create_follow_up_task'],
        'approval_required_actions': ['send_message', 'edit_lead_data'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
    'approval-bot': {
        'scope_actions': ['summarize_approval_context', 'recommend_approval_decision', 'report_pending_approvals'],
        'approval_required_actions': ['change_deal_stage', 'send_message', 'trigger_external_webhook'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
    'content-bot': {
        'scope_actions': ['draft_message', 'draft_follow_up_copy', 'draft_case_study_snippet'],
        'approval_required_actions': ['send_message', 'trigger_external_webhook'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
    'ads-bot': {
        'scope_actions': ['summarize_campaign_signal', 'tag_lead_origin', 'report_media_feedback'],
        'approval_required_actions': ['edit_lead_data', 'trigger_external_webhook'],
        'owners': ['Sergio Castro', 'Marco Alevato'],
    },
}

KILL_SWITCH_PREFIX = 'agents:kill_switch'


def validate_agent_repository(repository_path: str) -> AgentValidationOut:
    candidate = Path(repository_path)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate

    missing_files = [file_name for file_name in REQUIRED_AGENT_FILES if not (candidate / file_name).exists()]
    return AgentValidationOut(
        repository_path=str(candidate),
        valid=not missing_files,
        missing_files=missing_files,
    )



def _resolve_repository_path(repository_path: str) -> Path:
    candidate = Path(repository_path)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    return candidate



def _read_repository_git_sha(repository_path: Path) -> str:
    try:
        completed = subprocess.run(
            ['git', '-C', str(repository_path), 'rev-parse', 'HEAD'],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        sha = completed.stdout.strip()
        return sha or 'unversioned'
    except (subprocess.SubprocessError, FileNotFoundError):
        return 'unversioned'


async def sync_agent_markdown_cache(pool: Pool, workspace_id: UUID, agent_id: UUID, repository_path: str) -> AgentMarkdownCacheListOut:
    candidate = _resolve_repository_path(repository_path)
    git_sha = _read_repository_git_sha(candidate)
    records: list[AgentMarkdownCacheOut] = []

    for file_name in REQUIRED_AGENT_FILES:
        file_path = candidate / file_name
        content = file_path.read_text(encoding='utf-8')
        row = await pool.fetchrow(
            """
            INSERT INTO agent_markdown_cache (workspace_id, agent_id, file_name, git_sha, content, repository_path, refreshed_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
            ON CONFLICT (agent_id, file_name)
            DO UPDATE SET
                git_sha = EXCLUDED.git_sha,
                content = EXCLUDED.content,
                repository_path = EXCLUDED.repository_path,
                refreshed_at = NOW()
            RETURNING id, workspace_id, agent_id, file_name, git_sha, content, repository_path, refreshed_at, updated_at
            """,
            workspace_id,
            agent_id,
            file_name,
            git_sha,
            content,
            str(candidate),
        )
        records.append(AgentMarkdownCacheOut(**dict(row)))

    return AgentMarkdownCacheListOut(files=records)


async def list_agent_markdown_cache(pool: Pool, workspace_id: UUID) -> AgentMarkdownCacheListOut:
    rows = await pool.fetch(
        """
        SELECT id, workspace_id, agent_id, file_name, git_sha, content, repository_path, refreshed_at, updated_at
        FROM agent_markdown_cache
        WHERE workspace_id = $1
        ORDER BY repository_path, file_name
        """,
        workspace_id,
    )
    return AgentMarkdownCacheListOut(files=[AgentMarkdownCacheOut(**dict(row)) for row in rows])


def _kill_switch_key(workspace_id: UUID) -> str:
    return f'{KILL_SWITCH_PREFIX}:{workspace_id}'


def _policy_for_slug(slug: str) -> dict[str, object]:
    return AGENT_POLICIES.get(slug, {})


def _derive_heartbeat_status(last_heartbeat_at: datetime | None) -> str:
    if last_heartbeat_at is None:
        return 'offline'
    delta = datetime.now(timezone.utc) - last_heartbeat_at
    if delta.total_seconds() <= 90:
        return 'online'
    if delta.total_seconds() <= 300:
        return 'stale'
    return 'offline'


def _agent_out_from_row(row: object, control: AgentControlOut) -> AgentOut:
    data = dict(row)
    policy = _policy_for_slug(data['slug'])
    return AgentOut(
        **data,
        scope_actions=policy.get('scope_actions', []),
        approval_required_actions=policy.get('approval_required_actions', []),
        owners=policy.get('owners', []),
        kill_switch_active=control.kill_switch_active,
        last_heartbeat_at=data.get('last_heartbeat_at'),
        heartbeat_status=_derive_heartbeat_status(data.get('last_heartbeat_at')),
    )


async def _get_agent_row(pool: Pool, workspace_id: UUID, agent_id: UUID) -> object | None:
    return await pool.fetchrow(
        'SELECT id, slug, display_name, status, repository_url, last_heartbeat_at FROM agents WHERE id = $1 AND workspace_id = $2',
        agent_id,
        workspace_id,
    )


async def _broadcast_workspace_event(workspace_id: UUID, event: str, payload: dict[str, object]) -> None:
    await workspace_manager.broadcast(str(workspace_id), event, payload)


async def _create_agent_task(
    connection: object,
    *,
    workspace_id: UUID,
    deal_id: UUID | None,
    channel_id: UUID | None,
    title: str,
    description: str,
    priority: str = 'high',
) -> UUID:
    row = await connection.fetchrow(
        """
        INSERT INTO tasks (workspace_id, deal_id, channel_id, title, description, priority, source)
        VALUES ($1, $2, $3, $4, $5, $6, 'agent')
        RETURNING id
        """,
        workspace_id,
        deal_id,
        channel_id,
        sanitize_text(title) or title,
        sanitize_text(description) or description,
        priority,
    )
    task_id = row['id']
    task_payload = {
        'task_id': str(task_id),
        'source': 'agent',
        'deal_id': str(deal_id) if deal_id else None,
        'channel_id': str(channel_id) if channel_id else None,
    }
    if channel_id is not None:
        await manager.broadcast(str(channel_id), 'task_created', {'task_id': str(task_id), 'source': 'agent'})
    await _broadcast_workspace_event(workspace_id, 'task_created', task_payload)
    return task_id


async def _create_agent_message(
    connection: object,
    *,
    workspace_id: UUID,
    channel_id: UUID,
    agent_id: UUID,
    body: str,
    source_system: str = 'agent-api',
) -> UUID:
    row = await connection.fetchrow(
        """
        INSERT INTO messages (workspace_id, channel_id, author_type, author_id, body, source_system)
        VALUES ($1, $2, 'agent', $3, $4, $5)
        RETURNING id
        """,
        workspace_id,
        channel_id,
        str(agent_id),
        sanitize_text(body) or body,
        source_system,
    )
    message_id = row['id']
    message_payload = {
        'message_id': str(message_id),
        'channel_id': str(channel_id),
        'author_type': 'agent',
        'source_system': source_system,
    }
    await manager.broadcast(str(channel_id), 'message_created', {'message_id': str(message_id), 'author_type': 'agent'})
    await _broadcast_workspace_event(workspace_id, 'message_created', message_payload)
    return message_id


async def _consume_approved_action(
    connection: object,
    *,
    workspace_id: UUID,
    approval_id: UUID,
    agent_id: UUID,
    action_type: str,
) -> None:
    row = await connection.fetchrow(
        'SELECT id, agent_id, action_type, status, payload FROM approvals WHERE id = $1 AND workspace_id = $2',
        approval_id,
        workspace_id,
    )
    if row is None:
        raise ValueError('Approval not found for agent execution.')
    if row['agent_id'] != agent_id:
        raise ValueError('Approval does not belong to this agent.')
    if row['action_type'] != action_type:
        raise ValueError('Approval action does not match requested action.')
    if row['status'] != 'approved':
        raise ValueError('Approval is not approved yet.')

    approval_payload = row['payload'] if isinstance(row['payload'], dict) else json.loads(row['payload'])
    if approval_payload.get('_executed_at'):
        raise ValueError('Approval was already consumed by a previous execution.')

    approval_payload['_executed_at'] = datetime.now(timezone.utc).isoformat()
    await connection.execute(
        'UPDATE approvals SET payload = $1::jsonb WHERE id = $2 AND workspace_id = $3',
        json.dumps(approval_payload),
        approval_id,
        workspace_id,
    )


async def _execute_scoped_action(
    connection: object,
    *,
    workspace_id: UUID,
    agent_id: UUID,
    action_type: str,
    payload: dict[str, object],
) -> tuple[str, UUID | None, UUID | None]:
    if action_type == 'create_follow_up_task':
        deal_id_raw = payload.get('deal_id')
        title = str(payload.get('title') or 'Fazer follow-up comercial')
        description = str(payload.get('description') or 'Tarefa criada por agente para continuidade do deal.')
        channel_id = None
        deal_id = None
        if deal_id_raw:
            deal_id = UUID(str(deal_id_raw))
            deal = await connection.fetchrow(
                'SELECT id, channel_id FROM deals WHERE id = $1 AND workspace_id = $2',
                deal_id,
                workspace_id,
            )
            if deal is None:
                raise ValueError('Deal not found for follow-up task.')
            channel_id = deal['channel_id']
        task_id = await _create_agent_task(
            connection,
            workspace_id=workspace_id,
            deal_id=deal_id,
            channel_id=channel_id,
            title=title,
            description=description,
            priority=str(payload.get('priority') or 'high'),
        )
        return 'Task created successfully.', task_id, None

    if action_type == 'suggest_stage_change':
        deal_id_raw = payload.get('deal_id')
        if not deal_id_raw:
            raise ValueError('deal_id is required for suggest_stage_change.')
        target_stage_raw = str(payload.get('target_stage') or '').strip()
        if not target_stage_raw:
            raise ValueError('target_stage is required for suggest_stage_change.')
        target_stage = normalize_stage(target_stage_raw)
        if target_stage not in CANONICAL_STAGES:
            raise ValueError('Invalid target_stage.')
        reason = str(payload.get('reason') or 'Sugestao automatica de proxima etapa comercial.')
        deal = await connection.fetchrow(
            'SELECT id, company_name, stage, channel_id FROM deals WHERE id = $1 AND workspace_id = $2',
            UUID(str(deal_id_raw)),
            workspace_id,
        )
        if deal is None:
            raise ValueError('Deal not found for stage suggestion.')
        title = f'Revisar mudanca de stage para {target_stage}'
        description = (
            f"Deal: {deal['company_name']}\n"
            f"Stage atual: {deal['stage']}\n"
            f"Stage sugerido: {target_stage}\n"
            f"Motivo: {reason}"
        )
        task_id = await _create_agent_task(
            connection,
            workspace_id=workspace_id,
            deal_id=deal['id'],
            channel_id=deal['channel_id'],
            title=title,
            description=description,
            priority='high',
        )
        message_id = None
        if deal['channel_id'] is not None:
            message_id = await _create_agent_message(
                connection,
                workspace_id=workspace_id,
                channel_id=deal['channel_id'],
                agent_id=agent_id,
                body=f'Sugestao de stage para {target_stage} registrada para revisao humana.',
            )
        return 'Stage suggestion recorded for human review.', task_id, message_id

    if action_type == 'draft_message':
        channel_id_raw = payload.get('channel_id')
        deal_id_raw = payload.get('deal_id')
        draft_body = str(payload.get('body') or '').strip()
        if not draft_body:
            raise ValueError('body is required for draft_message.')
        channel_id = None
        if channel_id_raw:
            channel_id = UUID(str(channel_id_raw))
        elif deal_id_raw:
            deal = await connection.fetchrow(
                'SELECT channel_id FROM deals WHERE id = $1 AND workspace_id = $2',
                UUID(str(deal_id_raw)),
                workspace_id,
            )
            if deal is None or deal['channel_id'] is None:
                raise ValueError('Channel not found for draft_message.')
            channel_id = deal['channel_id']
        else:
            raise ValueError('channel_id or deal_id is required for draft_message.')

        message_id = await _create_agent_message(
            connection,
            workspace_id=workspace_id,
            channel_id=channel_id,
            agent_id=agent_id,
            body=f'Rascunho sugerido: {draft_body}',
            source_system='agent-draft',
        )
        return 'Draft message recorded in channel.', None, message_id

    return 'Action accepted and recorded in the audit log.', None, None


async def get_agent_control(workspace_id: UUID) -> AgentControlOut:
    redis = get_redis_client()
    raw = await redis.get(_kill_switch_key(workspace_id))
    if not raw:
        return AgentControlOut(workspace_id=workspace_id)
    payload = json.loads(raw)
    return AgentControlOut(
        workspace_id=workspace_id,
        kill_switch_active=bool(payload.get('active', False)),
        reason=payload.get('reason'),
        updated_by_user_id=UUID(payload['updated_by_user_id']) if payload.get('updated_by_user_id') else None,
        updated_at=datetime.fromisoformat(payload['updated_at']) if payload.get('updated_at') else None,
    )


async def set_kill_switch(workspace_id: UUID, user_id: UUID, payload: AgentControlUpdateRequest) -> AgentControlOut:
    redis = get_redis_client()
    data = {
        'active': payload.active,
        'reason': payload.reason,
        'updated_by_user_id': str(user_id),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    await redis.set(_kill_switch_key(workspace_id), json.dumps(data))
    control = await get_agent_control(workspace_id)
    await _broadcast_workspace_event(
        workspace_id,
        'kill_switch_updated',
        {
            'active': control.kill_switch_active,
            'reason': control.reason,
            'updated_by_user_id': str(control.updated_by_user_id) if control.updated_by_user_id else None,
            'updated_at': control.updated_at.isoformat() if control.updated_at else None,
        },
    )
    return control


def _coerce_json_object(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    return {}


def _parse_approval(row: object) -> ApprovalOut:
    data = dict(row)
    payload = _coerce_json_object(data.get('payload'))

    requested_by_user_id = payload.get('_requested_by_user_id')
    resolved_by_user_id = payload.get('_resolved_by_user_id')
    decision_notes = payload.get('_decision_notes')
    expires_at_raw = payload.get('_expires_at')
    expires_at = datetime.fromisoformat(expires_at_raw) if isinstance(expires_at_raw, str) else None
    expired = bool(data['status'] == 'pending' and expires_at and expires_at <= datetime.now(timezone.utc))
    public_payload = {key: value for key, value in payload.items() if not key.startswith('_')}

    return ApprovalOut(
        id=data['id'],
        workspace_id=data['workspace_id'],
        agent_id=data['agent_id'],
        action_type=data['action_type'],
        status='expired' if expired else data['status'],
        requested_by_user_id=UUID(requested_by_user_id) if requested_by_user_id else None,
        resolved_by_user_id=UUID(resolved_by_user_id) if resolved_by_user_id else None,
        decision_notes=decision_notes if isinstance(decision_notes, str) else None,
        expires_at=expires_at,
        expired=expired,
        payload=public_payload,
        requested_at=data['requested_at'],
        resolved_at=data['resolved_at'],
    )


def _parse_audit_log(row: object) -> AuditLogOut:
    data = dict(row)
    return AuditLogOut(
        id=data['id'],
        workspace_id=data['workspace_id'],
        agent_id=data['agent_id'],
        action_type=data['action_type'],
        trigger_type=data['trigger_type'],
        payload=_coerce_json_object(data.get('payload')),
        result=_coerce_json_object(data.get('result')),
        created_at=data['created_at'],
    )


async def list_agents(pool: Pool, workspace_id: UUID) -> AgentListOut:
    control = await get_agent_control(workspace_id)
    rows = await pool.fetch(
        'SELECT id, slug, display_name, status, repository_url, last_heartbeat_at FROM agents WHERE workspace_id = $1 ORDER BY display_name',
        workspace_id,
    )
    return AgentListOut(agents=[_agent_out_from_row(row, control) for row in rows])


async def register_agent(pool: Pool, workspace_id: UUID, payload: AgentRegistrationRequest) -> AgentRegistrationOut:
    validation = validate_agent_repository(payload.repository_path)
    if not validation.valid:
        raise ValueError(', '.join(validation.missing_files))

    row = await pool.fetchrow(
        """
        INSERT INTO agents (workspace_id, slug, display_name, status, repository_url)
        VALUES ($1, $2, $3, 'online', $4)
        ON CONFLICT (workspace_id, slug)
        DO UPDATE SET display_name = EXCLUDED.display_name, repository_url = EXCLUDED.repository_url, status = 'online'
        RETURNING id, slug, display_name, status, repository_url, last_heartbeat_at
        """,
        workspace_id,
        payload.slug,
        payload.display_name,
        validation.repository_path,
    )
    control = await get_agent_control(workspace_id)
    agent = _agent_out_from_row(row, control)
    await sync_agent_markdown_cache(pool, workspace_id, agent.id, validation.repository_path)
    await _broadcast_workspace_event(
        workspace_id,
        'agent_registered',
        {'agent_id': str(agent.id), 'slug': agent.slug, 'display_name': agent.display_name, 'status': agent.status},
    )
    return AgentRegistrationOut(agent=agent, validation=validation)


async def issue_agent_token(pool: Pool, workspace_id: UUID, requested_by_user_id: UUID, payload: AgentTokenRequest) -> AgentTokenOut:
    row = await _get_agent_row(pool, workspace_id, payload.agent_id)
    if row is None:
        raise ValueError('Agent not found.')
    control = await get_agent_control(workspace_id)
    agent = _agent_out_from_row(row, control)
    if agent.repository_url:
        await sync_agent_markdown_cache(pool, workspace_id, agent.id, agent.repository_url)
    access_token, expires_at = create_agent_access_token(
        agent_id=agent.id,
        workspace_id=workspace_id,
        slug=agent.slug,
        scope_actions=agent.scope_actions,
        approval_required_actions=agent.approval_required_actions,
        ttl_minutes=payload.ttl_minutes,
    )
    await get_redis_client().set(
        build_agent_token_cache_key(access_token),
        str(agent.id),
        ex=24 * 60 * 60,
    )
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='agent_token_issued',
        trigger_type='api',
        payload={
            'agent_id': str(agent.id),
            'requested_by_user_id': str(requested_by_user_id),
            'ttl_minutes': payload.ttl_minutes,
        },
        result={'status': 'issued', 'expires_at': expires_at.isoformat()},
    )
    return AgentTokenOut(access_token=access_token, expires_at=expires_at, agent=agent)


async def record_agent_heartbeat(pool: Pool, workspace_id: UUID, agent_id: UUID, status: str) -> AgentHeartbeatOut:
    row = await pool.fetchrow(
        """
        UPDATE agents
        SET status = $1, last_heartbeat_at = NOW()
        WHERE id = $2 AND workspace_id = $3
        RETURNING id, workspace_id, status, last_heartbeat_at
        """,
        status,
        agent_id,
        workspace_id,
    )
    if row is None:
        raise ValueError('Agent not found.')

    payload = {
        'agent_id': str(row['id']),
        'status': row['status'],
        'last_heartbeat_at': row['last_heartbeat_at'].isoformat(),
    }
    await _broadcast_workspace_event(workspace_id, 'agent_heartbeat', payload)
    return AgentHeartbeatOut(
        agent_id=row['id'],
        workspace_id=row['workspace_id'],
        status=row['status'],
        last_heartbeat_at=row['last_heartbeat_at'],
    )


async def list_approvals(pool: Pool, workspace_id: UUID) -> ApprovalListOut:
    rows = await pool.fetch(
        'SELECT id, workspace_id, agent_id, action_type, status, payload, requested_at, resolved_at FROM approvals WHERE workspace_id = $1 ORDER BY requested_at DESC',
        workspace_id,
    )
    return ApprovalListOut(approvals=[_parse_approval(row) for row in rows])


async def create_approval(pool: Pool, workspace_id: UUID, requested_by_user_id: UUID, payload: ApprovalCreateRequest) -> ApprovalOut:
    control = await get_agent_control(workspace_id)
    if control.kill_switch_active:
        raise ValueError('Kill switch is active for this workspace.')

    if payload.agent_id is not None:
        agent = await pool.fetchrow(
            'SELECT slug FROM agents WHERE id = $1 AND workspace_id = $2',
            payload.agent_id,
            workspace_id,
        )
        if agent is None:
            raise ValueError('Agent not found.')
        policy = _policy_for_slug(agent['slug'])
        allowed_actions = set(policy.get('scope_actions', [])) | set(policy.get('approval_required_actions', []))
        if payload.action_type not in allowed_actions:
            raise ValueError(f'Action {payload.action_type} is outside the scope of {agent["slug"]}.')

    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    approval_payload = {
        **payload.payload,
        '_requested_by_user_id': str(requested_by_user_id),
        '_expires_at': expires_at.isoformat(),
    }
    row = await pool.fetchrow(
        "INSERT INTO approvals (workspace_id, agent_id, action_type, status, payload) VALUES ($1, $2, $3, 'pending', $4::jsonb) RETURNING id, workspace_id, agent_id, action_type, status, payload, requested_at, resolved_at",
        workspace_id,
        payload.agent_id,
        payload.action_type,
        json.dumps(approval_payload),
    )
    approval = _parse_approval(row)
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='approval_requested',
        trigger_type='api',
        payload={
            **payload.model_dump(mode='json'),
            'requested_by_user_id': str(requested_by_user_id),
            'expires_at': expires_at.isoformat(),
        },
        result={'approval_id': str(approval.id), 'status': approval.status},
    )
    await _broadcast_workspace_event(
        workspace_id,
        'approval_created',
        {'approval_id': str(approval.id), 'action_type': approval.action_type, 'status': approval.status},
    )
    return approval


async def decide_approval(
    pool: Pool,
    workspace_id: UUID,
    approval_id: UUID,
    resolved_by_user_id: UUID,
    payload: ApprovalDecisionRequest,
) -> ApprovalOut:
    current = await pool.fetchrow(
        'SELECT id, workspace_id, agent_id, action_type, status, payload, requested_at, resolved_at FROM approvals WHERE id = $1 AND workspace_id = $2',
        approval_id,
        workspace_id,
    )
    if current is None:
        raise ValueError('Approval not found.')

    approval = _parse_approval(current)
    if approval.status != 'pending':
        raise ValueError(f'Approval is already {approval.status}.')

    merged_payload = {
        **approval.payload,
        '_requested_by_user_id': str(approval.requested_by_user_id) if approval.requested_by_user_id else None,
        '_expires_at': approval.expires_at.isoformat() if approval.expires_at else None,
        '_resolved_by_user_id': str(resolved_by_user_id),
        '_decision_notes': payload.decision_notes,
    }
    row = await pool.fetchrow(
        """
        UPDATE approvals
        SET status = $1, resolved_at = NOW(), payload = $2::jsonb
        WHERE id = $3 AND workspace_id = $4
        RETURNING id, workspace_id, agent_id, action_type, status, payload, requested_at, resolved_at
        """,
        payload.status,
        json.dumps(merged_payload),
        approval_id,
        workspace_id,
    )
    approval = _parse_approval(row)
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='approval_decided',
        trigger_type='api',
        payload={
            'approval_id': str(approval_id),
            **payload.model_dump(mode='json'),
            'resolved_by_user_id': str(resolved_by_user_id),
        },
        result={'status': approval.status},
    )
    await _broadcast_workspace_event(
        workspace_id,
        'approval_decided',
        {'approval_id': str(approval.id), 'action_type': approval.action_type, 'status': approval.status},
    )
    return approval


async def execute_agent_action(
    pool: Pool,
    *,
    workspace_id: UUID,
    agent_id: UUID,
    agent_slug: str,
    token_scope_actions: list[str],
    token_approval_required_actions: list[str],
    action_type: str,
    payload: dict[str, object],
) -> AgentExecutionOut:
    control = await get_agent_control(workspace_id)
    if control.kill_switch_active:
        raise ValueError('Kill switch is active for this workspace.')

    row = await _get_agent_row(pool, workspace_id, agent_id)
    if row is None:
        raise ValueError('Agent not found.')

    policy = _policy_for_slug(agent_slug)
    allowed_actions = set(policy.get('scope_actions', [])) | set(policy.get('approval_required_actions', []))
    token_allowed_actions = set(token_scope_actions) | set(token_approval_required_actions)
    if action_type not in allowed_actions:
        raise ValueError(f'Action {action_type} is outside the scope of {agent_slug}.')
    if action_type not in token_allowed_actions:
        raise ValueError(f'Action {action_type} is not authorized by the current agent token.')

    if action_type in set(policy.get('approval_required_actions', [])):
        approval_id_raw = payload.get('approval_id')
        if action_type != 'change_deal_stage' or not approval_id_raw:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            approval_payload = {
                **payload,
                '_requested_by_agent_id': str(agent_id),
                '_expires_at': expires_at.isoformat(),
            }
            approval_row = await pool.fetchrow(
                "INSERT INTO approvals (workspace_id, agent_id, action_type, status, payload) VALUES ($1, $2, $3, 'pending', $4::jsonb) RETURNING id",
                workspace_id,
                agent_id,
                action_type,
                json.dumps(approval_payload),
            )
            approval_id = approval_row['id']
            await log_agent_action(
                pool=pool,
                workspace_id=workspace_id,
                agent_id=agent_id,
                action_type=action_type,
                trigger_type='agent_api',
                payload=payload,
                result={'status': 'approval_required', 'approval_id': str(approval_id)},
            )
            await _broadcast_workspace_event(
                workspace_id,
                'approval_created',
                {'approval_id': str(approval_id), 'action_type': action_type, 'status': 'pending'},
            )
            return AgentExecutionOut(
                status='approval_required',
                agent_id=agent_id,
                workspace_id=workspace_id,
                action_type=action_type,
                approval_id=approval_id,
                task_id=None,
                message_id=None,
                audit_log_status='logged',
                message='Action requires human approval before execution.',
            )

        async with pool.acquire() as connection:
            async with connection.transaction():
                await _consume_approved_action(
                    connection,
                    workspace_id=workspace_id,
                    approval_id=UUID(str(approval_id_raw)),
                    agent_id=agent_id,
                    action_type=action_type,
                )
                transition = await execute_stage_transition(
                    connection,
                    workspace_id,
                    UUID(str(payload.get('deal_id'))),
                    stage=str(payload.get('stage') or ''),
                    reason_code=str(payload.get('reason_code')) if payload.get('reason_code') else None,
                    reason_notes=str(payload.get('reason_notes')) if payload.get('reason_notes') else None,
                    changed_by_type='agent',
                )
                await log_agent_action(
                    pool=connection,
                    workspace_id=workspace_id,
                    agent_id=agent_id,
                    action_type=action_type,
                    trigger_type='agent_api',
                    payload=payload,
                    result={
                        'status': 'executed',
                        'deal_id': str(transition['deal'].id),
                        'stage': transition['deal'].stage,
                        'delivery': transition['delivery'],
                    },
                )

        return AgentExecutionOut(
            status='executed',
            agent_id=agent_id,
            workspace_id=workspace_id,
            action_type=action_type,
            approval_id=UUID(str(approval_id_raw)),
            task_id=None,
            message_id=None,
            audit_log_status='logged',
            message='Approved deal stage change executed successfully.',
        )

    async with pool.acquire() as connection:
        async with connection.transaction():
            execution_message, task_id, message_id = await _execute_scoped_action(
                connection,
                workspace_id=workspace_id,
                agent_id=agent_id,
                action_type=action_type,
                payload=payload,
            )
            await log_agent_action(
                pool=connection,
                workspace_id=workspace_id,
                agent_id=agent_id,
                action_type=action_type,
                trigger_type='agent_api',
                payload=payload,
                result={
                    'status': 'executed',
                    'task_id': str(task_id) if task_id else None,
                    'message_id': str(message_id) if message_id else None,
                },
            )

    return AgentExecutionOut(
        status='executed',
        agent_id=agent_id,
        workspace_id=workspace_id,
        action_type=action_type,
        approval_id=None,
        task_id=task_id,
        message_id=message_id,
        audit_log_status='logged',
        message=execution_message,
    )


async def list_audit_logs(pool: Pool, workspace_id: UUID) -> AuditLogListOut:
    rows = await pool.fetch(
        'SELECT id, workspace_id, agent_id, action_type, trigger_type, payload, result, created_at FROM agent_action_logs WHERE workspace_id = $1 ORDER BY created_at DESC LIMIT 100',
        workspace_id,
    )
    return AuditLogListOut(logs=[_parse_audit_log(row) for row in rows])






