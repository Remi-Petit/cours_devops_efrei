from fastapi import HTTPException
from sqlalchemy import text
from app.config.connect_db import AsyncSessionLocal

async def config():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM config ORDER BY key"))
            rows = result.mappings().all()
        return {
            "count": len(rows),
            "data": rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
