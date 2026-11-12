"""数据库引擎与会话。

- FastAPI 使用 async engine（asyncpg）；
- Alembic / Celery Worker 使用 sync engine（psycopg），同一调用链不混用。
"""

from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

async_engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# 同步引擎供 Alembic 与 Celery Worker 使用
sync_engine = create_engine(settings.database_url_sync, echo=False, pool_pre_ping=True)
sync_session_factory = sessionmaker(sync_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供请求级异步会话。"""
    async with async_session_factory() as session:
        yield session
