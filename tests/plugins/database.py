from contextlib import asynccontextmanager
from typing import TypeVar

import pytest
from mimesis import Schema
from sqlalchemy.ext.asyncio import AsyncSession

DBInstanceType = TypeVar('DBInstanceType')


@pytest.fixture()
def database(test_app):
    yield test_app.adapters_container.database()


@pytest.fixture()
def insert_query_factory(test_session):
    async def factory(instance: DBInstanceType) -> DBInstanceType:
        test_session.add(instance)
        await test_session.flush()
        return instance

    return factory


@pytest.fixture()
async def test_session(envs, test_app) -> AsyncSession:
    db = test_app.adapters_container.database()
    connection = await db.engine.connect()
    transaction = await connection.begin()
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    yield async_session
    await async_session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture()
def session_manager(test_session):
    @asynccontextmanager
    async def manager():
        try:
            yield test_session
        except Exception:
            await test_session.rollback()
            raise
        finally:
            ...

    return manager


@pytest.fixture()
def generate_schema():
    def inner(schema):
        return Schema(
            schema=lambda: schema,
            iterations=1,
        ).create()[0]
    return inner
