import asyncio
import logging
from typing import List, Dict, Any

from sqlalchemy import MetaData, Table, Column, Text
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert

# Ensure project root is on sys.path so that 'app' package can be imported when running this file directly
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

# Reuse the async engine and sessionmaker configured in the app
from app.config.connect_db import engine, AsyncSessionLocal


logger = logging.getLogger(__name__)

# Define metadata and table schema (SQLAlchemy Core)
metadata = MetaData()

config_table = Table(
	"config",
	metadata,
	Column("key", Text, primary_key=True),
	Column("value", JSONB, nullable=False),
	schema="public",
)


async def create_schema() -> None:
	"""Create database schema objects (idempotent)."""
	logger.info("Creating schema (if not exists)...")
	async with engine.begin() as conn:
		# run_sync executes synchronous DDL helpers in the async context
		await conn.run_sync(metadata.create_all)
	logger.info("Schema creation complete.")


def seed_payload() -> List[Dict[str, Any]]:
	"""Return the initial seed rows for public.config."""
	return [
		{
			"key": "app.name",
			"value": {"service": "lastmetro-api", "version": "1.0.0"},
		},
		{
			"key": "metro.defaults",
			"value": {"line": "M1", "headwayMin": 5, "timezone": "Europe/Paris"},
		},
		{
			"key": "station.chatelet",
			"value": {
				"name": "Châtelet",
				"lines": ["M1", "M4", "M7", "M11", "M14"],
				"lastMetro": "00:40",
			},
		},
	]


async def seed_data() -> None:
	"""Insert initial data into public.config (idempotent)."""
	rows = seed_payload()
	if not rows:
		logger.info("No seed data to insert.")
		return

	logger.info("Seeding data into public.config (ON CONFLICT DO NOTHING)...")
	async with AsyncSessionLocal() as session:
		stmt = pg_insert(config_table).values(rows).on_conflict_do_nothing()
		await session.execute(stmt)
		await session.commit()
	logger.info("Seed insert complete.")


async def main() -> None:
	try:
		await create_schema()
		await seed_data()
		print("✅ Database initialization completed successfully.")
	except Exception as exc:
		logger.exception("❌ Database initialization failed: %s", exc)
		raise


if __name__ == "__main__":
	asyncio.run(main())