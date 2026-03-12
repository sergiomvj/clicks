from uuid import UUID

from asyncpg import Pool

from app.agents.action_logger import log_platform_action
from app.git_watcher.schemas import GitWatcherListOut, GitWatcherOut, GitWatcherUpsertRequest


async def list_git_watchers(pool: Pool, workspace_id: UUID) -> GitWatcherListOut:
    rows = await pool.fetch(
        "SELECT id, workspace_id, agent_id, repository_path, branch, status, last_seen_commit, last_synced_at, last_error, created_at, updated_at FROM git_watchers WHERE workspace_id = $1 ORDER BY updated_at DESC, repository_path",
        workspace_id,
    )
    return GitWatcherListOut(watchers=[GitWatcherOut(**dict(row)) for row in rows])


async def upsert_git_watcher(pool: Pool, workspace_id: UUID, payload: GitWatcherUpsertRequest) -> GitWatcherOut:
    row = await pool.fetchrow(
        """
        INSERT INTO git_watchers (workspace_id, agent_id, repository_path, branch, status, last_seen_commit, last_synced_at, last_error)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (workspace_id, repository_path)
        DO UPDATE SET
            agent_id = EXCLUDED.agent_id,
            branch = EXCLUDED.branch,
            status = EXCLUDED.status,
            last_seen_commit = EXCLUDED.last_seen_commit,
            last_synced_at = EXCLUDED.last_synced_at,
            last_error = EXCLUDED.last_error,
            updated_at = NOW()
        RETURNING id, workspace_id, agent_id, repository_path, branch, status, last_seen_commit, last_synced_at, last_error, created_at, updated_at
        """,
        workspace_id,
        payload.agent_id,
        payload.repository_path,
        payload.branch,
        payload.status,
        payload.last_seen_commit,
        payload.last_synced_at,
        payload.last_error,
    )
    watcher = GitWatcherOut(**dict(row))
    await log_platform_action(
        pool=pool,
        workspace_id=workspace_id,
        action_type='git_watcher_upserted',
        trigger_type='api',
        payload=payload.model_dump(mode='json'),
        result={'git_watcher_id': str(watcher.id), 'status': watcher.status},
    )
    return watcher
