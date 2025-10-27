import os
from functools import lru_cache
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv pas installé
    pass

class Settings:
    def __init__(self) -> None:
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres_lastmetro")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        
        # Validation des variables critiques
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_USER et POSTGRES_PASSWORD sont obligatoires")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()