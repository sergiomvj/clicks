import json
from uuid import UUID

from asyncpg import Pool


async def log_agent_action(
    pool: Pool,
    workspace_id: UUID,
    agent_id: UUID | None,
    action_type: str,
    trigger_type: str,
    payload: dict[str, object],
    result: dict[str, object],
) -> None:
    await pool.execute(
        "INSERT INTO agent_action_logs (workspace_id, agent_id, action_type, trigger_type, payload, result) VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)",
        workspace_id,
        agent_id,
        action_type,
        trigger_type,
        json.dumps(payload),
        json.dumps(result),
    )


async def log_platform_action(
    pool: Pool,
    workspace_id: UUID,
    action_type: str,
    trigger_type: str,
    payload: dict[str, object],
    result: dict[str, object],
) -> None:
    await log_agent_action(
        pool=pool,
        workspace_id=workspace_id,
        agent_id=None,
        action_type=action_type,
        trigger_type=trigger_type,
        payload=payload,
        result=result,
    )
