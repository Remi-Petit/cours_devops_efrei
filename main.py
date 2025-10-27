from typing import Union
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

# Middleware pour le logging basique (équivalent du logger Express)
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = int((time.time() - start_time) * 1000)
        print(f"{request.method} {request.url.path} -> {response.status_code} ({process_time}ms)")
        return response

app.add_middleware(LoggingMiddleware)

# ENDPOINT 1 : Health check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "lastmetro-api",
        "timestamp": datetime.now().isoformat()
    }

# ENDPOINT 2 : Calculer le prochain métro
@app.get("/next-metro")
def next_metro(station: Union[str, None] = None):
    # Validation
    if not station:
        raise HTTPException(status_code=400, detail="missing station parameter")
    
    # Simulation : ajouter 5 minutes à l'heure actuelle
    now = datetime.now()
    next_time = now + timedelta(minutes=5)
    next_time_str = next_time.strftime("%H:%M")
    
    return {
        "station": station,
        "line": "M1",
        "nextArrival": next_time_str,
        "headwayMin": 5
    }

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 3000))
    print(f"🚇 Last Metro API démarrée sur http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/health")
    uvicorn.run(app, host="0.0.0.0", port=PORT)