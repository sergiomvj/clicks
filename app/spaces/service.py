from uuid import UUID

from asyncpg import Pool

from app.spaces.schemas import ChannelOut, SpaceBundle, SpaceOut


async def list_spaces_bundle(pool: Pool, workspace_id: UUID) -> SpaceBundle:
    space_rows = await pool.fetch("SELECT id, workspace_id, slug, name FROM spaces WHERE workspace_id = $1 ORDER BY name", workspace_id)
    channel_rows = await pool.fetch("SELECT id, workspace_id, space_id, slug, name, channel_type FROM channels WHERE workspace_id = $1 ORDER BY name", workspace_id)
    return SpaceBundle(
        spaces=[SpaceOut(**dict(row)) for row in space_rows],
        channels=[ChannelOut(**dict(row)) for row in channel_rows],
    )
