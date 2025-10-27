from fastapi import FastAPI
import os
import uvicorn
from app.routes import health, metro
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

# Ajouter le middleware de logging
app.add_middleware(LoggingMiddleware)

# Inclure les routes
app.include_router(health.router)
app.include_router(metro.router)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 3000))
    print(f"🚇 Last Metro API démarrée sur http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/health")
    uvicorn.run(app, host="0.0.0.0", port=PORT)