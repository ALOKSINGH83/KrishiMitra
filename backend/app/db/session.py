from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True) if settings.database_url else None
SessionLocal = async_sessionmaker(engine, expire_on_commit=False) if engine else None


async def get_db() -> AsyncIterator[AsyncSession]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with SessionLocal() as session:
        yield session
