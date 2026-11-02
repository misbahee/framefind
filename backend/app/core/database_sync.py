from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Sync engine for Celery workers.
# asyncpg is async-only, so we swap the driver to psycopg2 for sync use.
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")

sync_engine = create_engine(SYNC_DATABASE_URL)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

