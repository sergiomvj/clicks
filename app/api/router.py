from fastapi import APIRouter

from app.agents.agent_api_routes import router as agent_api_router
from app.agents.routes import router as agents_router
from app.crm.routes import router as crm_router
from app.git_watcher.routes import router as git_watcher_router
from app.kpis.routes import router as kpis_router
from app.messaging.routes import router as messaging_router
from app.spaces.routes import router as spaces_router
from app.tasks.routes import router as tasks_router
from app.webhooks.routes import legacy_router as webhooks_legacy_router
from app.webhooks.routes import router as webhooks_router

api_router = APIRouter(prefix='/api')
api_router.include_router(spaces_router)
api_router.include_router(kpis_router)
api_router.include_router(messaging_router)
api_router.include_router(tasks_router)
api_router.include_router(crm_router)
api_router.include_router(agents_router)
api_router.include_router(agent_api_router)
api_router.include_router(git_watcher_router)
api_router.include_router(webhooks_router)
api_router.include_router(webhooks_legacy_router)
