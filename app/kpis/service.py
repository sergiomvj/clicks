from uuid import UUID

from asyncpg import Pool

from app.kpis.schemas import KpiListOut, KpiOut


async def list_kpis(pool: Pool, workspace_id: UUID) -> KpiListOut:
    rows = await pool.fetch(
        """
        SELECT id, workspace_id, space_id, slug, name, unit, target_value, current_value, status, source, updated_at
        FROM kpis
        WHERE workspace_id = $1
        ORDER BY name
        """,
        workspace_id,
    )
    return KpiListOut(kpis=[KpiOut(**dict(row)) for row in rows])
