import pytest
from dependency_injector import providers

from src.modules.tasks.repository import TasksRepository
from src.modules.tasks.service import TasksService


@pytest.fixture(scope='session')
def repositories_container():
    from src.containers import RepositoriesContainer
    return RepositoriesContainer()


@pytest.fixture(scope='session')
def services_container():
    from src.containers import ServicesContainer
    return ServicesContainer()


@pytest.fixture()
def tasks_repository(
    repositories_container,
):
    with repositories_container.tasks_repository.override(
        providers.Factory(
            TasksRepository,
        )
    ):
        repository = repositories_container.tasks_repository
        yield repository()


@pytest.fixture()
def tasks_service(
    services_container,
    session_manager,
    tasks_repository,
):
    with services_container.tasks_service.override(
        providers.Factory(
            TasksService,
            session_factory=session_manager,
            tasks_repository=tasks_repository,
        )
    ):
        service = services_container.tasks_service
        yield service()
