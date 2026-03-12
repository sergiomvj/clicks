from uuid import UUID

from asyncpg import Pool

from app.agents.websocket import workspace_manager
from app.core.sanitization import sanitize_text
from app.messaging.schemas import MessageCreate, MessageListOut, MessageOut
from app.messaging.websocket import manager


async def list_messages(pool: Pool, workspace_id: UUID, channel_id: UUID) -> MessageListOut:
    rows = await pool.fetch(
        "SELECT id, channel_id, author_type, author_id, body, source_system, created_at FROM messages WHERE workspace_id = $1 AND channel_id = $2 ORDER BY created_at DESC LIMIT 50",
        workspace_id,
        channel_id,
    )
    messages = [MessageOut(**dict(row)) for row in rows]
    messages.reverse()
    return MessageListOut(messages=messages)


async def create_message(pool: Pool, workspace_id: UUID, user_id: UUID, payload: MessageCreate) -> MessageOut:
    body = sanitize_text(payload.body) or ''
    row = await pool.fetchrow(
        "INSERT INTO messages (workspace_id, channel_id, author_type, author_id, body) VALUES ($1, $2, 'human', $3, $4) RETURNING id, channel_id, author_type, author_id, body, source_system, created_at",
        workspace_id,
        UUID(payload.channel_id),
        str(user_id),
        body,
    )
    message = MessageOut(**dict(row))
    message_payload = {
        'message_id': str(message.id),
        'channel_id': str(message.channel_id),
        'author_type': message.author_type,
        'source_system': message.source_system,
    }
    await manager.broadcast(str(message.channel_id), 'message_created', {'message_id': str(message.id), 'author_type': message.author_type})
    await workspace_manager.broadcast(str(workspace_id), 'message_created', message_payload)
    return message
