from datetime import datetime
from app.config.connect_db import test_connection

async def health_check():
    db_status = await test_connection()
    return {
        "status": "ok" if db_status else "error",
        "db": "up" if db_status else "down",
        "service": "lastmetro-api",
        "timestamp": datetime.now().isoformat()
    }