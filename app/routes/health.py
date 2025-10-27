from fastapi import APIRouter
from app.controllers.health import health_check

router = APIRouter()

@router.get("/health")
async def get_health_check():
    return await health_check()