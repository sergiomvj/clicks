from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.webhooks.schemas import FbrClickWebhookPayload, PostalWebhookPayload, WebhookAckResponse
from app.webhooks.service import WebhookSecurityError, WebhookService, get_webhook_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/postal", response_model=WebhookAckResponse)
async def handle_postal_webhook(
    request: Request,
    payload: PostalWebhookPayload,
    webhook_service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> WebhookAckResponse:
    body = await request.body()
    try:
        webhook_service.verify_hmac(body, x_signature, webhook_service.get_postal_secret())
    except WebhookSecurityError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return await webhook_service.process_postal(payload)


@router.post("/fbr-click", response_model=WebhookAckResponse)
async def handle_fbr_click_webhook(
    request: Request,
    payload: FbrClickWebhookPayload,
    webhook_service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> WebhookAckResponse:
    body = await request.body()
    try:
        webhook_service.verify_hmac(body, x_signature, webhook_service.get_fbr_click_secret())
    except WebhookSecurityError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return await webhook_service.process_fbr_click(payload)
