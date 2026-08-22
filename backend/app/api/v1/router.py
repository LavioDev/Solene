from fastapi import APIRouter
from app.api.v1.auth_router import router as auth_router
from app.api.v1.device_router import router as device_router
from app.api.v1.event_router import router as event_router
from app.api.v1.note_router import router as note_router
from app.api.v1.media_router import router as media_router
from app.api.v1.task_router import router as task_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(device_router)
api_v1_router.include_router(event_router)
api_v1_router.include_router(note_router)
api_v1_router.include_router(media_router)
api_v1_router.include_router(task_router)

