import json

import httpx

from app.core.config import get_settings
from app.core.security import build_hmac_signature
from app.integrations.schemas import FbrEcosystemCallback


def _resolve_callback_url(raw_url: str, fallback_path: str) -> str:
    base = raw_url.strip().rstrip('/')
    if not base:
        return ''
    if base.endswith('/webhook'):
        return base
    return f'{base}{fallback_path}'


async def _post_signed_callback(callback_url: str, secret: str, payload: dict[str, object]) -> dict[str, object]:
    if not callback_url:
        return {'status': 'skipped', 'reason': 'missing_callback_url'}

    body = json.dumps(payload).encode('utf-8')
    signature = build_hmac_signature(body, secret)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                callback_url,
                content=body,
                headers={
                    'Content-Type': 'application/json',
                    'X-Signature': signature,
                },
            )
        return {
            'status': 'delivered' if response.is_success else 'failed',
            'callback_url': callback_url,
            'http_status': response.status_code,
            'response_body': response.text[:500],
        }
    except Exception as exc:
        return {
            'status': 'failed',
            'callback_url': callback_url,
            'error': str(exc),
        }


async def send_stage_event_to_fbr_leads(event: dict[str, object]) -> dict[str, object]:
    settings = get_settings()
    callback_url = _resolve_callback_url(settings.fbr_leads_api_url, '/api/v1/leads/webhook')
    return await _post_signed_callback(callback_url, settings.fbr_leads_webhook_secret, event)


async def send_callback_to_fbr_dev(event: FbrEcosystemCallback) -> dict[str, object]:
    settings = get_settings()
    callback_url = _resolve_callback_url(settings.fbr_dev_api_url, '/api/v1/events/webhook')
    return await _post_signed_callback(callback_url, settings.fbr_dev_webhook_secret, event.model_dump(mode='json'))


async def send_callback_to_fbr_suporte(event: FbrEcosystemCallback) -> dict[str, object]:
    settings = get_settings()
    callback_url = _resolve_callback_url(settings.fbr_suporte_api_url, '/api/v1/handoff/webhook')
    return await _post_signed_callback(callback_url, settings.fbr_suporte_webhook_secret, event.model_dump(mode='json'))
