from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker
    )

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)