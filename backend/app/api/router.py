"""Versioned API router aggregating all sub-routers."""
from fastapi import APIRouter

from app.api.cases import router as cases_router
from app.api.credibility import router as credibility_router
from app.api.events import router as events_router
from app.api.feeds import router as feeds_router
from app.api.tags import router as tags_router

api_router = APIRouter()

api_router.include_router(cases_router)
api_router.include_router(events_router)
api_router.include_router(credibility_router)
api_router.include_router(tags_router)
api_router.include_router(feeds_router)
