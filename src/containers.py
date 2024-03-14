from dependency_injector import containers, providers

from src.adapters.database import Database
from src.modules.tasks.repository import TasksRepository
from src.modules.tasks.service import TasksService


class AdaptersContainer(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.db_models",
        ],
    )
    config = providers.Configuration()
    database = providers.Singleton(
        Database,
        db_url=config.database.url
    )
    session = database.provided.async_session


class RepositoriesContainer(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.db_models", "src.modules"
        ],
    )
    adapters: AdaptersContainer = providers.Container(container_cls=AdaptersContainer)
    tasks_repository: TasksRepository = providers.Factory(
        TasksRepository,
    )


class ServicesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=['src.db_models', 'src.modules'],
        modules=[
            "src.db_models",
            "src.modules",
        ],
    )
    adapters: AdaptersContainer = providers.Container(container_cls=AdaptersContainer)
    repositories: RepositoriesContainer = providers.Container(
        RepositoriesContainer,
    )
    tasks_service: TasksService = providers.Factory(
        TasksService,
        tasks_repository=repositories.tasks_repository,
        session_factory=adapters.session,
    )
