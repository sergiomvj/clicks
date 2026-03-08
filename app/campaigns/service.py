from uuid import UUID

from asyncpg import Record

from app.core.database import get_database_pool
from app.campaigns.schemas import (
    CampaignCreateRequest,
    CampaignDispatchRequest,
    CampaignDispatchResponse,
    CampaignResponse,
    DispatchItemResponse,
    GeneratedEmailResponse,
)


class CampaignService:
    async def list_campaigns(self, workspace_id: UUID) -> list[CampaignResponse]:
        database_pool = get_database_pool()
        rows = await database_pool.fetch(
            """
            SELECT id, workspace_id, icp_profile_id, name, status, created_at, updated_at
            FROM campaigns
            WHERE workspace_id = $1
            ORDER BY created_at DESC
            """,
            workspace_id,
        )
        return [self._to_campaign_response(row) for row in rows]

    async def create_campaign(
        self,
        workspace_id: UUID,
        payload: CampaignCreateRequest,
    ) -> CampaignResponse:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            INSERT INTO campaigns (workspace_id, icp_profile_id, name, status)
            VALUES ($1, $2, $3, 'draft')
            RETURNING id, workspace_id, icp_profile_id, name, status, created_at, updated_at
            """,
            workspace_id,
            payload.icp_profile_id,
            payload.name,
        )
        if row is None:
            raise RuntimeError("Campaign insert failed.")
        return self._to_campaign_response(row)

    async def write_email(
        self,
        workspace_id: UUID,
        campaign_id: UUID,
    ) -> GeneratedEmailResponse:
        campaign = await self._require_campaign(workspace_id, campaign_id)
        subject = f"Ideia para {campaign['name']} sem aumentar o volume do time"
        body = (
            "Oi, tudo bem?\n\n"
            "Notei sinais de crescimento no seu mercado e montei uma ideia de abordagem "
            "para gerar mais conversas qualificadas sem depender de prospeccao manual.\n\n"
            "Se fizer sentido, posso te mostrar em 15 minutos como isso se encaixa na rotina atual.\n\n"
            "Abraco"
        )
        return GeneratedEmailResponse(
            campaign=self._to_campaign_response(campaign),
            subject=subject,
            body=body,
        )

    async def dispatch_campaign(
        self,
        workspace_id: UUID,
        campaign_id: UUID,
        payload: CampaignDispatchRequest,
    ) -> CampaignDispatchResponse:
        database_pool = get_database_pool()
        campaign = await self._require_campaign(workspace_id, campaign_id)
        domain = await database_pool.fetchrow(
            """
            SELECT id, daily_limit, sends_today
            FROM domains
            WHERE workspace_id = $1
              AND is_active = true
              AND is_blacklisted = false
              AND sends_today < daily_limit
            ORDER BY reputation_score DESC, warm_phase DESC, created_at ASC
            LIMIT 1
            """,
            workspace_id,
        )
        if domain is None:
            raise LookupError("No active domain available for dispatch.")

        dispatched: list[DispatchItemResponse] = []
        async with database_pool.acquire() as connection:
            async with connection.transaction():
                for lead_id in payload.lead_ids:
                    lead = await connection.fetchrow(
                        """
                        SELECT id
                        FROM leads
                        WHERE id = $1 AND workspace_id = $2
                        """,
                        lead_id,
                        workspace_id,
                    )
                    if lead is None:
                        continue
                    await connection.execute(
                        """
                        INSERT INTO email_sends (lead_id, domain_id, status, sent_at)
                        VALUES ($1, $2, 'sent', now())
                        """,
                        lead_id,
                        domain["id"],
                    )
                    await connection.execute(
                        """
                        UPDATE leads
                        SET campaign_id = $3,
                            funnel_stage = 'warming'
                        WHERE id = $1 AND workspace_id = $2
                        """,
                        lead_id,
                        workspace_id,
                        campaign_id,
                    )
                    await connection.execute(
                        """
                        UPDATE domains
                        SET sends_today = sends_today + 1
                        WHERE id = $1
                        """,
                        domain["id"],
                    )
                    dispatched.append(
                        DispatchItemResponse(
                            lead_id=lead_id,
                            domain_id=domain["id"],
                            status="sent",
                        )
                    )
        return CampaignDispatchResponse(
            campaign=self._to_campaign_response(campaign),
            dispatched=dispatched,
        )

    async def _require_campaign(self, workspace_id: UUID, campaign_id: UUID) -> Record:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            SELECT id, workspace_id, icp_profile_id, name, status, created_at, updated_at
            FROM campaigns
            WHERE id = $1 AND workspace_id = $2
            """,
            campaign_id,
            workspace_id,
        )
        if row is None:
            raise LookupError("Campaign not found.")
        return row

    def _to_campaign_response(self, row: Record) -> CampaignResponse:
        return CampaignResponse(
            id=row["id"],
            workspace_id=row["workspace_id"],
            icp_profile_id=row["icp_profile_id"],
            name=row["name"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


def get_campaign_service() -> CampaignService:
    return CampaignService()
