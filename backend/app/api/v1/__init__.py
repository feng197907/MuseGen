"""v1 API route aggregator."""
from fastapi import APIRouter
from app.api.v1.projects import router as projects_router
from app.api.v1.storyboards import router as storyboards_router
from app.api.v1.assets import router as assets_router
from app.api.v1.generate import router as generate_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.export import router as export_router
from app.api.v1.sse import router as sse_router

router = APIRouter()

router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(storyboards_router, prefix="/storyboards", tags=["Storyboards"])
router.include_router(assets_router, prefix="/assets", tags=["Assets"])
router.include_router(generate_router, prefix="/generate", tags=["Generate"])
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
router.include_router(export_router, prefix="/export", tags=["Export"])
router.include_router(sse_router, prefix="/sse", tags=["SSE"])
