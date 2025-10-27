from fastapi import FastAPI
from app.routes import health, metro, config
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

# Ajouter le middleware de logging
app.add_middleware(LoggingMiddleware)

# Inclure les routes
app.include_router(health.router)
app.include_router(metro.router)
app.include_router(config.router)