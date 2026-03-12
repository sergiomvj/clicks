from uuid import UUID

from asyncpg import Pool

from app.agents.websocket import workspace_manager
from app.messaging.websocket import manager
from app.tasks.schemas import TaskCreate, TaskListOut, TaskOut


async def list_tasks(pool: Pool, workspace_id: UUID) -> TaskListOut:
    rows = await pool.fetch("SELECT id, title, status, priority, source, due_at FROM tasks WHERE workspace_id = $1 ORDER BY created_at DESC", workspace_id)
    return TaskListOut(tasks=[TaskOut(**dict(row)) for row in rows])


async def create_task(pool: Pool, workspace_id: UUID, payload: TaskCreate) -> TaskOut:
    deal_id = UUID(payload.deal_id) if payload.deal_id else None
    channel_id = UUID(payload.channel_id) if payload.channel_id else None
    row = await pool.fetchrow(
        "INSERT INTO tasks (workspace_id, deal_id, channel_id, title, description, priority, source) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, title, status, priority, source, due_at",
        workspace_id,
        deal_id,
        channel_id,
        payload.title,
        payload.description,
        payload.priority,
        payload.source,
    )
    task = TaskOut(**dict(row))
    if channel_id is not None:
        await manager.broadcast(str(channel_id), 'task_created', {'task_id': str(task.id), 'source': task.source})
    await workspace_manager.broadcast(
        str(workspace_id),
        'task_created',
        {
            'task_id': str(task.id),
            'source': task.source,
            'deal_id': str(deal_id) if deal_id else None,
            'channel_id': str(channel_id) if channel_id else None,
        },
    )
    return task
