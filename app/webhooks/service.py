import hashlib
import hmac
import json
from datetime import datetime, timezone
from uuid import UUID

from app.core.config import get_settings
from app.core.database import get_database_pool
from app.webhooks.schemas import FbrClickWebhookPayload, PostalWebhookPayload, WebhookAckResponse


class WebhookSecurityError(Exception):
    pass


class WebhookService:
    def verify_hmac(self, body: bytes, signature: str | None, secret: str) -> None:
        if signature is None:
            raise WebhookSecurityError("Missing signature.")
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, signature):
            raise WebhookSecurityError("Invalid signature.")

    async def process_postal(self, payload: PostalWebhookPayload) -> WebhookAckResponse:
        database_pool = get_database_pool()
        async with database_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    """
                    INSERT INTO interactions (lead_id, email_send_id, type, metadata)
                    VALUES ($1, $2, $3, $4::jsonb)
                    """,
                    payload.lead_id,
                    payload.email_send_id,
                    self._map_postal_event(payload.event),
                    json.dumps(payload.metadata),
                )
                if payload.event == "bounce":
                    await connection.execute(
                        """
                        UPDATE leads
                        SET funnel_stage = 'discard',
                            discard_reason = 'postal_bounce'
                        WHERE id = $1
                        """,
                        payload.lead_id,
                    )
        return WebhookAckResponse(status="ok", processed_at=datetime.now(timezone.utc))

    async def process_fbr_click(self, payload: FbrClickWebhookPayload) -> WebhookAckResponse:
        database_pool = get_database_pool()
        report_content = json.dumps(payload.metadata | {"reason": payload.reason})
        async with database_pool.acquire() as connection:
            async with connection.transaction():
                if payload.lead_id is not None:
                    stage = "sql" if payload.event == "deal.won" else "discard"
                    await connection.execute(
                        """
                        UPDATE leads
                        SET funnel_stage = $2,
                            discard_reason = $3
                        WHERE id = $1
                        """,
                        payload.lead_id,
                        stage,
                        payload.reason,
                    )
                if payload.campaign_id is not None:
                    workspace_row = await connection.fetchrow(
                        "SELECT workspace_id FROM campaigns WHERE id = $1",
                        payload.campaign_id,
                    )
                    if workspace_row is not None:
                        await connection.execute(
                            """
                            INSERT INTO intelligence_reports (workspace_id, campaign_id, content, insights)
                            VALUES ($1, $2, $3::jsonb, $4)
                            """,
                            workspace_row["workspace_id"],
                            payload.campaign_id,
                            report_content,
                            f"Feedback recebido: {payload.event}",
                        )
        return WebhookAckResponse(status="ok", processed_at=datetime.now(timezone.utc))

    def get_postal_secret(self) -> str:
        return get_settings().postal_webhook_secret

    def get_fbr_click_secret(self) -> str:
        return get_settings().fbr_click_webhook_secret

    def _map_postal_event(self, event: str) -> str:
        mapping = {
            "open": "open",
            "click": "click",
            "reply": "reply",
            "bounce": "bounce",
        }
        return mapping.get(event, "reply")


def get_webhook_service() -> WebhookService:
    return WebhookService()
