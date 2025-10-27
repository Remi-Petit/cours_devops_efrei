from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.config.env import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

# ENGINE ASYNCHRONE
try:
    engine = create_async_engine(
        _settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        echo=False,
    )
    
    logger.info("✅ Engine asyncpg créé avec succès")
    
except Exception as e:
    logger.error(f"❌ Erreur création engine: {e}")
    raise

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, autocommit=False)

# DEPENDENCY ASYNCHRONE
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Erreur de session DB: {e}")
            await db.rollback()
            raise

# Fonction utilitaire pour tester la connexion
async def test_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Test de connexion échoué: {e}")
        return False