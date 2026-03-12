from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import close_database_pool, open_database_pool
from app.core.llm import get_llm_service
from app.core.redis import close_redis_client, open_redis_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await open_database_pool(settings)
    await open_redis_client(settings)
    yield
    await close_redis_client()
    await close_database_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="FBR-CLICK API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_workspace_header(request: Request, call_next):
        is_internal_api = request.url.path.startswith("/api/")
        is_public_webhook = request.url.path.startswith("/api/webhooks") or request.url.path.startswith("/api/v1/")
        if is_internal_api and not is_public_webhook:
            workspace_id = request.headers.get("X-Workspace-Id", "").strip()
            if not workspace_id:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "X-Workspace-Id header is required."})
        return await call_next(request)

    @app.get("/health")
    async def healthcheck() -> dict[str, object]:
        payload = await get_llm_service().get_health_payload()
        payload["lead_sources"] = ["fbr_leads", "social_media", "product_site", "manual", "support", "other"]
        payload["upstream_priority"] = "1FBR-Leads"
        return payload

    app.include_router(api_router)
    return app


app = create_app()
