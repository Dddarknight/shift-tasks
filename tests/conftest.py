import pytest_asyncio
from dependency_injector import providers

from src.adapters.database import Database


@pytest_asyncio.fixture(autouse=True)
async def mock_db(
    envs, test_app
):
    test_db_dependency = providers.Singleton(
        Database, db_url=envs.database.test_url)
    with test_app.adapters_container.database.override(test_db_dependency):
        db = test_app.adapters_container.database()
        await db.create_database()
        yield
        await db.drop_database()
