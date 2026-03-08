from decimal import Decimal
from uuid import UUID

from asyncpg import Record

from app.core.database import get_database_pool
from app.domains.schemas import (
    DomainCreateRequest,
    DomainHealthCheckResponse,
    DomainPhaseUpdateRequest,
    DomainResponse,
)


class DomainService:
    async def list_domains(self, workspace_id: UUID) -> list[DomainResponse]:
        database_pool = get_database_pool()
        rows = await database_pool.fetch(
            """
            SELECT id, workspace_id, domain, warm_phase, daily_limit, sends_today,
                   reputation_score, bounce_rate, is_blacklisted, is_active
            FROM domains
            WHERE workspace_id = $1
            ORDER BY created_at DESC
            """,
            workspace_id,
        )
        return [self._to_domain_response(row) for row in rows]

    async def create_domain(
        self,
        workspace_id: UUID,
        payload: DomainCreateRequest,
    ) -> DomainResponse:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            INSERT INTO domains (
                workspace_id,
                domain,
                warm_phase,
                daily_limit,
                warm_started_at
            )
            VALUES ($1, $2, $3, $4, now())
            RETURNING id, workspace_id, domain, warm_phase, daily_limit, sends_today,
                      reputation_score, bounce_rate, is_blacklisted, is_active
            """,
            workspace_id,
            payload.domain,
            payload.warm_phase,
            payload.daily_limit,
        )
        if row is None:
            raise RuntimeError("Domain insert failed.")
        return self._to_domain_response(row)

    async def update_phase(
        self,
        workspace_id: UUID,
        domain_id: UUID,
        payload: DomainPhaseUpdateRequest,
    ) -> DomainResponse:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            UPDATE domains
            SET warm_phase = $3,
                is_active = true
            WHERE id = $1 AND workspace_id = $2
            RETURNING id, workspace_id, domain, warm_phase, daily_limit, sends_today,
                      reputation_score, bounce_rate, is_blacklisted, is_active
            """,
            domain_id,
            workspace_id,
            payload.warm_phase,
        )
        if row is None:
            raise LookupError("Domain not found.")
        return self._to_domain_response(row)

    async def check_blacklist(
        self,
        workspace_id: UUID,
        domain_id: UUID,
    ) -> DomainHealthCheckResponse:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            SELECT id, domain, is_blacklisted, is_active, reputation_score, bounce_rate
            FROM domains
            WHERE id = $1 AND workspace_id = $2
            """,
            domain_id,
            workspace_id,
        )
        if row is None:
            raise LookupError("Domain not found.")
        health_status = self._get_health_status(
            reputation_score=row["reputation_score"],
            bounce_rate=row["bounce_rate"],
            is_blacklisted=row["is_blacklisted"],
            is_active=row["is_active"],
        )
        return DomainHealthCheckResponse(
            id=row["id"],
            domain=row["domain"],
            is_blacklisted=row["is_blacklisted"],
            is_active=row["is_active"],
            reputation_score=row["reputation_score"],
            bounce_rate=float(row["bounce_rate"]),
            health_status=health_status,
        )

    def _to_domain_response(self, row: Record) -> DomainResponse:
        return DomainResponse(
            id=row["id"],
            workspace_id=row["workspace_id"],
            domain=row["domain"],
            warm_phase=row["warm_phase"],
            daily_limit=row["daily_limit"],
            sends_today=row["sends_today"],
            reputation_score=row["reputation_score"],
            bounce_rate=float(row["bounce_rate"]),
            is_blacklisted=row["is_blacklisted"],
            is_active=row["is_active"],
            health_status=self._get_health_status(
                reputation_score=row["reputation_score"],
                bounce_rate=row["bounce_rate"],
                is_blacklisted=row["is_blacklisted"],
                is_active=row["is_active"],
            ),
        )

    def _get_health_status(
        self,
        reputation_score: int,
        bounce_rate: Decimal,
        is_blacklisted: bool,
        is_active: bool,
    ) -> str:
        if is_blacklisted or not is_active:
            return "critical"
        if bounce_rate > Decimal("2.00") or reputation_score < 80:
            return "alert"
        return "healthy"


def get_domain_service() -> DomainService:
    return DomainService()
