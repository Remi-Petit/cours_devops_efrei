from fastapi import APIRouter, HTTPException
from app.controllers.config import config

router = APIRouter()

@router.get("/config")
async def get_config():
    try:
        return await config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
