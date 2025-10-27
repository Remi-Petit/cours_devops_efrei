from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "lastmetro-api",
        "timestamp": datetime.now().isoformat()
    }