from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy import create_engine, AsyncAdaptedQueuePool, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.ddl import CreateSchema

from config import get_settings


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base:
    __allow_unmapped__ = True


Base = declarative_base(cls=Base, metadata=meta)
autoload_engine = create_engine(get_settings().database.url)
Base.metadata.bind = autoload_engine


AsyncSessionManager = Callable[..., AbstractAsyncContextManager[AsyncSession]]


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url, poolclass=AsyncAdaptedQueuePool)
        self._session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(
        self
    ) -> AsyncSessionManager:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def async_session(self) -> AsyncSessionManager:
        session: AsyncSession = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(CreateSchema('public', if_not_exists=True))
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @property
    def engine(self):
        return self._engine
