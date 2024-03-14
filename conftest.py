import sys
import os
import pytest
from httpx import AsyncClient
from src.server import app, settings
from dotenv import load_dotenv


load_dotenv()
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


tasks_plugins = [
    'tests.plugins.containers',
    'tests.plugins.database',
    'tests.plugins.factories',
]

pytest_plugins = [
    *tasks_plugins,
]


HOST = os.getenv("HOST")
APP_PORT = os.getenv("APP_PORT")


@pytest.fixture
def test_app():
    return app


@pytest.fixture()
def async_client(test_app):
    yield AsyncClient(app=test_app, base_url=f"http://{HOST}:{APP_PORT}")


@pytest.fixture(scope='session')
def envs():
    return settings
