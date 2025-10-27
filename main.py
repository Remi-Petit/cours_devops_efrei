from fastapi import FastAPI
from app.routes import health, metro, config
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

# Ajouter le middleware de logging
app.add_middleware(LoggingMiddleware)

# Endpoint racine pour lister les endpoints disponibles
@app.get("/")
async def root():
	return {
		"service": "lastmetro-api",
		"message": "Bienvenue sur l'API Last Metro",
		"endpoints": [
			{"method": "GET", "path": "/health", "description": "Etat du service et de la base"},
			{"method": "GET", "path": "/next-metro?station=Chatelet", "description": "Prochain passage (simulation +5 min)"},
			{"method": "GET", "path": "/config", "description": "Configuration depuis la base"},
			{"method": "GET", "path": "/docs", "description": "Swagger UI"},
			{"method": "GET", "path": "/redoc", "description": "ReDoc"},
		],
	}

# Inclure les routes
app.include_router(health.router)
app.include_router(metro.router)
app.include_router(config.router)