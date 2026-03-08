import json
from uuid import UUID

from app.core.database import get_database_pool


class ActionLogger:
    async def log_action(
        self,
        workspace_id: UUID,
        agent_id: str,
        team: str,
        action_type: str,
        trigger_type: str,
        payload: dict[str, object],
        result: dict[str, object] | None = None,
        error: str | None = None,
    ) -> None:
        database_pool = get_database_pool()
        await database_pool.execute(
            """
            INSERT INTO agent_action_logs (
                workspace_id,
                agent_id,
                team,
                action_type,
                trigger_type,
                payload,
                result,
                error
            )
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb, $8)
            """,
            workspace_id,
            agent_id,
            team,
            action_type,
            trigger_type,
            json.dumps(payload),
            json.dumps(result) if result is not None else None,
            error,
        )


def get_action_logger() -> ActionLogger:
    return ActionLogger()
