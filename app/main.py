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
    app = FastAPI(title="FBR-Leads API", version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_agent_header(request: Request, call_next):
        if request.url.path.startswith("/api/"):
            agent_id = request.headers.get("X-Agent-Id", "").strip()
            if not agent_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "X-Agent-Id header is required."},
                )
        return await call_next(request)

    @app.get("/health")
    async def healthcheck() -> dict[str, object]:
        llm_service = get_llm_service()
        return await llm_service.get_health_payload()

    app.include_router(api_router)
    return app
