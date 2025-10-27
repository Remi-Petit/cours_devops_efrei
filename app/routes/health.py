from fastapi import APIRouter
from app.controllers.health import health_check

router = APIRouter()

@router.get("/health")
def get_health_check():
    return health_check()