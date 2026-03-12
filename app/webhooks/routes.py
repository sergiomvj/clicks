from fastapi import APIRouter, Header, Request

from app.core.database import get_database_pool
from app.core.rate_limit import enforce_rate_limit
from app.core.security import get_webhook_secret, verify_hmac_signature
from app.webhooks.schemas import AcceptedStatusOut, FbrDevEventPayload, FbrSuporteLeadPayload, GenericWebhookAck, LeadHandoffPayload, LeadHandoffResult
from app.webhooks.service import process_fbr_dev_event, process_fbr_leads_handoff, process_fbr_suporte_handoff

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
legacy_router = APIRouter(prefix="/v1", tags=["webhooks-v1"])


@router.post("/fbr-leads/handoff", response_model=LeadHandoffResult)
async def receive_fbr_leads_handoff(request: Request, payload: LeadHandoffPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> LeadHandoffResult:
    await enforce_rate_limit('webhooks:fbr_leads', limit=120, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_leads"), x_signature)
    return await process_fbr_leads_handoff(get_database_pool(), payload)


@legacy_router.post("/leads/webhook", response_model=AcceptedStatusOut)
async def receive_fbr_leads_handoff_v1(request: Request, payload: LeadHandoffPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> AcceptedStatusOut:
    await enforce_rate_limit('webhooks:fbr_leads_v1', limit=120, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_leads"), x_signature)
    await process_fbr_leads_handoff(get_database_pool(), payload)
    return AcceptedStatusOut(status='accepted')


@router.post("/fbr-dev/events", response_model=GenericWebhookAck)
async def receive_fbr_dev_event(request: Request, payload: FbrDevEventPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> GenericWebhookAck:
    await enforce_rate_limit('webhooks:fbr_dev', limit=180, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_dev"), x_signature)
    return await process_fbr_dev_event(get_database_pool(), payload)


@legacy_router.post("/dev/events/webhook", response_model=AcceptedStatusOut)
async def receive_fbr_dev_event_v1(request: Request, payload: FbrDevEventPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> AcceptedStatusOut:
    await enforce_rate_limit('webhooks:fbr_dev_v1', limit=180, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_dev"), x_signature)
    await process_fbr_dev_event(get_database_pool(), payload)
    return AcceptedStatusOut(status='accepted')


@router.post("/fbr-suporte/handoff", response_model=GenericWebhookAck)
async def receive_fbr_suporte_handoff(request: Request, payload: FbrSuporteLeadPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> GenericWebhookAck:
    await enforce_rate_limit('webhooks:fbr_suporte', limit=120, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_suporte"), x_signature)
    return await process_fbr_suporte_handoff(get_database_pool(), payload)


@legacy_router.post("/suporte/handoff/webhook", response_model=AcceptedStatusOut)
async def receive_fbr_suporte_handoff_v1(request: Request, payload: FbrSuporteLeadPayload, x_signature: str | None = Header(default=None, alias="X-Signature")) -> AcceptedStatusOut:
    await enforce_rate_limit('webhooks:fbr_suporte_v1', limit=120, window_seconds=60)
    await verify_hmac_signature(request, get_webhook_secret("fbr_suporte"), x_signature)
    await process_fbr_suporte_handoff(get_database_pool(), payload)
    return AcceptedStatusOut(status='accepted')
