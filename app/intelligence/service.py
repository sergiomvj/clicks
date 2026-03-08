from uuid import UUID

from asyncpg import Record

from app.core.database import get_database_pool
from app.intelligence.schemas import IntelligenceReportResponse


class IntelligenceService:
    async def get_latest_report(self, workspace_id: UUID) -> IntelligenceReportResponse:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            SELECT id, workspace_id, campaign_id, insights, generated_at, content
            FROM intelligence_reports
            WHERE workspace_id = $1
            ORDER BY generated_at DESC
            LIMIT 1
            """,
            workspace_id,
        )
        if row is None:
            raise LookupError("Report not found.")
        return self._to_report_response(row)

    def _to_report_response(self, row: Record) -> IntelligenceReportResponse:
        return IntelligenceReportResponse(
            id=row["id"],
            workspace_id=row["workspace_id"],
            campaign_id=row["campaign_id"],
            insights=row["insights"],
            generated_at=row["generated_at"],
            content=dict(row["content"]),
        )


def get_intelligence_service() -> IntelligenceService:
    return IntelligenceService()
