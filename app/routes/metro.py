from fastapi import APIRouter, HTTPException
from typing import Union
from datetime import datetime, timedelta
from app.controllers.metro import next_metro

router = APIRouter()

@router.get("/next-metro")
async def get_next_metro(station: Union[str, None] = None):
    return await next_metro(station=station)