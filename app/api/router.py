from fastapi import APIRouter

from app.campaigns.routes import router as campaigns_router
from app.domains.routes import router as domains_router
from app.intelligence.routes import router as intelligence_router
from app.leads.routes import router as leads_router
from app.webhooks.routes import router as webhooks_router

api_router = APIRouter(prefix="/api")
api_router.include_router(domains_router)
api_router.include_router(leads_router)
api_router.include_router(campaigns_router)
api_router.include_router(intelligence_router)
api_router.include_router(webhooks_router)
