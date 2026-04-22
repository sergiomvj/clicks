import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Header, HTTPException, Request, status
from jose import JWTError, jwt

from app.core.config import get_settings

AGENT_JWT_ALGORITHM = 'HS256'
AGENT_TOKEN_TTL_MINUTES = 24 * 60


async def require_user_id(x_user_id: str | None = Header(default=None)) -> str:
    if x_user_id is None or not x_user_id.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id header is required.")
    return x_user_id.strip()


async def require_workspace_id(x_workspace_id: str | None = Header(default=None)) -> str:
    if x_workspace_id is None or not x_workspace_id.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Workspace-Id header is required.")
    return x_workspace_id.strip()


async def require_agent_id(x_agent_id: str | None = Header(default=None)) -> str:
    if x_agent_id is None or not x_agent_id.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Agent-Id header is required.")
    return x_agent_id.strip()


async def require_bearer_token(authorization: str | None = Header(default=None, alias='Authorization')) -> str:
    if authorization is None or not authorization.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization header is required.')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Bearer token is required.')
    return token.strip()


def build_hmac_signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    return f'sha256={digest}'


async def verify_hmac_signature(request: Request, secret: str, signature: str | None) -> bytes:
    if signature is None or not signature.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing webhook signature.')

    body = await request.body()
    expected = build_hmac_signature(body, secret).replace('sha256=', '', 1)
    provided = signature.replace('sha256=', '', 1).strip()
    if not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid webhook signature.')
    return body


def get_webhook_secret(source: str) -> str:
    settings = get_settings()
    if source == 'fbr_leads':
        return settings.fbr_leads_webhook_secret
    if source == 'fbr_dev':
        return settings.fbr_dev_webhook_secret
    if source == 'fbr_suporte':
        return settings.fbr_suporte_webhook_secret
    raise RuntimeError(f'Unknown webhook source: {source}')


def build_agent_token_cache_key(token: str) -> str:
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    return f'agent:token:{token_hash}'


def create_agent_access_token(
    *,
    agent_id: UUID,
    workspace_id: UUID,
    slug: str,
    scope_actions: list[str],
    approval_required_actions: list[str],
    ttl_minutes: int = AGENT_TOKEN_TTL_MINUTES,
) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=AGENT_TOKEN_TTL_MINUTES)
    payload = {
        'sub': str(agent_id),
        'workspace_id': str(workspace_id),
        'slug': slug,
        'scope_actions': scope_actions,
        'approval_required_actions': approval_required_actions,
        'exp': int(expires_at.timestamp()),
        'iat': int(datetime.now(timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, settings.openclaw_agent_jwt_secret, algorithm=AGENT_JWT_ALGORITHM)
    return token, expires_at


def decode_agent_access_token(token: str) -> dict[str, object]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.openclaw_agent_jwt_secret, algorithms=[AGENT_JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid agent token.') from exc
    for required_field in ('sub', 'workspace_id', 'slug'):
        if required_field not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid agent token payload.')
    return payload
