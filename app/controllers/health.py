from datetime import datetime

def health_check():
    return {
        "status": "ok",
        "service": "lastmetro-api",
        "timestamp": datetime.now().isoformat()
    }