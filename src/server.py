from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import get_settings
from src.containers import AdaptersContainer, RepositoriesContainer, ServicesContainer
from src.modules.tasks.controllers import router_tasks

settings = get_settings()

adapters_container = AdaptersContainer()
adapters_container.config.from_dict(settings.model_dump())

repositories = RepositoriesContainer(adapters=adapters_container)
services = ServicesContainer(adapters=adapters_container, repositories=repositories)

app = FastAPI()
app.include_router(router_tasks)


app.adapters_container = adapters_container
app.repositories_container = repositories
app.services_container = services

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=settings.cors.headers,
)

db = adapters_container.database()


@app.on_event('startup')
async def startup():
    await db.create_database()
