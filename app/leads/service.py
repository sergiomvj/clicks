from collections.abc import Sequence
from uuid import UUID

from asyncpg import Record

from app.core.database import get_database_pool
from app.leads.schemas import (
    LeadDetailResponse,
    LeadIngestItem,
    LeadIngestRequest,
    LeadIngestResponse,
    LeadInteractionResponse,
    LeadResponse,
    LeadScoreResponse,
    LeadValidationResponse,
)


class LeadService:
    async def ingest_leads(
        self,
        workspace_id: UUID,
        payload: LeadIngestRequest,
    ) -> LeadIngestResponse:
        database_pool = get_database_pool()
        async with database_pool.acquire() as connection:
            async with connection.transaction():
                items = [
                    await self._insert_lead(connection, workspace_id, lead)
                    for lead in payload.leads
                ]
        return LeadIngestResponse(inserted_count=len(items), items=items)

    async def list_leads(
        self,
        workspace_id: UUID,
        stage: str | None,
        score_min: int | None,
        campaign_id: UUID | None,
        source: str | None,
    ) -> list[LeadResponse]:
        database_pool = get_database_pool()
        rows = await database_pool.fetch(
            """
            SELECT id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                   role, linkedin_url, company_name, company_cnpj, company_sector,
                   company_size, company_website, score, funnel_stage, source,
                   enrichment_data, discard_reason, created_at, updated_at
            FROM leads
            WHERE workspace_id = $1
              AND ($2::text IS NULL OR funnel_stage = $2)
              AND ($3::int IS NULL OR score >= $3)
              AND ($4::uuid IS NULL OR campaign_id = $4)
              AND ($5::text IS NULL OR source = $5)
            ORDER BY created_at DESC
            """,
            workspace_id,
            stage,
            score_min,
            campaign_id,
            source,
        )
        return [self._to_lead_response(row) for row in rows]

    async def get_lead_detail(
        self,
        workspace_id: UUID,
        lead_id: UUID,
    ) -> LeadDetailResponse:
        database_pool = get_database_pool()
        lead_row = await database_pool.fetchrow(
            """
            SELECT id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                   role, linkedin_url, company_name, company_cnpj, company_sector,
                   company_size, company_website, score, funnel_stage, source,
                   enrichment_data, discard_reason, created_at, updated_at
            FROM leads
            WHERE id = $1 AND workspace_id = $2
            """,
            lead_id,
            workspace_id,
        )
        if lead_row is None:
            raise LookupError("Lead not found.")
        interaction_rows = await database_pool.fetch(
            """
            SELECT id, type, occurred_at, metadata
            FROM interactions
            WHERE lead_id = $1
            ORDER BY occurred_at DESC
            """,
            lead_id,
        )
        interactions = [
            LeadInteractionResponse(
                id=row["id"],
                type=row["type"],
                occurred_at=row["occurred_at"],
                metadata=dict(row["metadata"]),
            )
            for row in interaction_rows
        ]
        return LeadDetailResponse(
            lead=self._to_lead_response(lead_row),
            interactions=interactions,
        )

    async def validate_email(
        self,
        workspace_id: UUID,
        lead_id: UUID,
    ) -> LeadValidationResponse:
        lead = await self._require_lead(workspace_id, lead_id)
        email = lead["email"] or ""
        is_valid = "@" in email and "." in email.split("@")[-1]
        funnel_stage = "validated" if is_valid else "discard"
        discard_reason = None if is_valid else "invalid_email"
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            UPDATE leads
            SET email_valid = $3,
                funnel_stage = $4,
                discard_reason = $5
            WHERE id = $1 AND workspace_id = $2
            RETURNING id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                      role, linkedin_url, company_name, company_cnpj, company_sector,
                      company_size, company_website, score, funnel_stage, source,
                      enrichment_data, discard_reason, created_at, updated_at
            """,
            lead_id,
            workspace_id,
            is_valid,
            funnel_stage,
            discard_reason,
        )
        if row is None:
            raise LookupError("Lead not found.")
        return LeadValidationResponse(lead=self._to_lead_response(row), is_valid=is_valid)

    async def enrich_lead(
        self,
        workspace_id: UUID,
        lead_id: UUID,
    ) -> LeadResponse:
        lead = await self._require_lead(workspace_id, lead_id)
        enrichment_data = dict(lead["enrichment_data"])
        inferred_website = self._infer_company_website(
            email=lead["email"],
            current_website=lead["company_website"],
        )
        if inferred_website is not None:
            enrichment_data["inferred_company_website"] = inferred_website
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            UPDATE leads
            SET company_website = COALESCE(company_website, $3),
                enrichment_data = $4::jsonb,
                funnel_stage = 'enriching'
            WHERE id = $1 AND workspace_id = $2
            RETURNING id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                      role, linkedin_url, company_name, company_cnpj, company_sector,
                      company_size, company_website, score, funnel_stage, source,
                      enrichment_data, discard_reason, created_at, updated_at
            """,
            lead_id,
            workspace_id,
            inferred_website,
            enrichment_data,
        )
        if row is None:
            raise LookupError("Lead not found.")
        return self._to_lead_response(row)

    async def score_lead(
        self,
        workspace_id: UUID,
        lead_id: UUID,
    ) -> LeadScoreResponse:
        lead = await self._require_lead(workspace_id, lead_id)
        score = self._calculate_score(lead)
        min_score = await self._get_min_score(lead["icp_profile_id"])
        funnel_stage = "qualified" if score >= min_score else "discard"
        discard_reason = None if score >= min_score else "below_min_score"
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            UPDATE leads
            SET score = $3,
                funnel_stage = $4,
                discard_reason = $5
            WHERE id = $1 AND workspace_id = $2
            RETURNING id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                      role, linkedin_url, company_name, company_cnpj, company_sector,
                      company_size, company_website, score, funnel_stage, source,
                      enrichment_data, discard_reason, created_at, updated_at
            """,
            lead_id,
            workspace_id,
            score,
            funnel_stage,
            discard_reason,
        )
        if row is None:
            raise LookupError("Lead not found.")
        reason = f"Scored {score} against min_score {min_score}."
        return LeadScoreResponse(lead=self._to_lead_response(row), score_reason=reason)

    async def _insert_lead(
        self,
        connection: object,
        workspace_id: UUID,
        lead: LeadIngestItem,
    ) -> LeadResponse:
        row = await connection.fetchrow(
            """
            INSERT INTO leads (
                workspace_id,
                campaign_id,
                icp_profile_id,
                name,
                email,
                role,
                linkedin_url,
                company_name,
                company_cnpj,
                company_sector,
                company_size,
                company_website,
                source
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                      role, linkedin_url, company_name, company_cnpj, company_sector,
                      company_size, company_website, score, funnel_stage, source,
                      enrichment_data, discard_reason, created_at, updated_at
            """,
            workspace_id,
            lead.campaign_id,
            lead.icp_profile_id,
            lead.name,
            lead.email,
            lead.role,
            lead.linkedin_url,
            lead.company_name,
            lead.company_cnpj,
            lead.company_sector,
            lead.company_size,
            lead.company_website,
            lead.source,
        )
        if row is None:
            raise RuntimeError("Lead insert failed.")
        return self._to_lead_response(row)

    async def _require_lead(self, workspace_id: UUID, lead_id: UUID) -> Record:
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            """
            SELECT id, workspace_id, campaign_id, icp_profile_id, name, email, email_valid,
                   role, linkedin_url, company_name, company_cnpj, company_sector,
                   company_size, company_website, score, funnel_stage, source,
                   enrichment_data, discard_reason, created_at, updated_at
            FROM leads
            WHERE id = $1 AND workspace_id = $2
            """,
            lead_id,
            workspace_id,
        )
        if row is None:
            raise LookupError("Lead not found.")
        return row

    async def _get_min_score(self, icp_profile_id: UUID | None) -> int:
        if icp_profile_id is None:
            return 60
        database_pool = get_database_pool()
        row = await database_pool.fetchrow(
            "SELECT min_score FROM icp_profiles WHERE id = $1",
            icp_profile_id,
        )
        if row is None:
            return 60
        return row["min_score"]

    def _to_lead_response(self, row: Record) -> LeadResponse:
        return LeadResponse(
            id=row["id"],
            workspace_id=row["workspace_id"],
            campaign_id=row["campaign_id"],
            icp_profile_id=row["icp_profile_id"],
            name=row["name"],
            email=row["email"],
            email_valid=row["email_valid"],
            role=row["role"],
            linkedin_url=row["linkedin_url"],
            company_name=row["company_name"],
            company_cnpj=row["company_cnpj"],
            company_sector=row["company_sector"],
            company_size=row["company_size"],
            company_website=row["company_website"],
            score=row["score"],
            funnel_stage=row["funnel_stage"],
            source=row["source"],
            enrichment_data=dict(row["enrichment_data"]),
            discard_reason=row["discard_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _infer_company_website(
        self,
        email: str | None,
        current_website: str | None,
    ) -> str | None:
        if current_website is not None:
            return current_website
        if email is None or "@" not in email:
            return None
        domain = email.split("@")[-1].strip().lower()
        if not domain:
            return None
        return f"https://{domain}"

    def _calculate_score(self, lead: Record) -> int:
        score = 0
        if lead["email_valid"]:
            score += 25
        if lead["linkedin_url"]:
            score += 20
        if lead["company_website"]:
            score += 20
        if lead["role"]:
            score += 15
        if lead["company_sector"]:
            score += 20
        return min(score, 100)


def get_lead_service() -> LeadService:
    return LeadService()
