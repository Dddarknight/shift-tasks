from datetime import date

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query

from src.containers import ServicesContainer
from src.modules.tasks.schemas import AddTaskModel, Task, AddProductModel, UpdateTaskModel
from src.modules.tasks.service import TasksService

router_tasks = APIRouter(prefix='/v1/tasks', tags=['Tasks'])


@inject
async def add_tasks(
    tasks: list[AddTaskModel],
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
):
    """Controller to add a task."""
    await service.add_task(
        tasks=tasks,
    )


router_tasks.add_api_route(
    path='',
    endpoint=add_tasks,
    summary="Adds a task.",
    methods=['POST'],
)


@inject
async def get_tasks(
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
    close_status: bool | None = Query(None),
    consignment_number: int | None = Query(None),
    consignment_date: date | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    offset: int = 0,
    limit: int = 30,
) -> list[Task]:
    """Controller to get tasks."""
    return await service.get_tasks(
        close_status=close_status,
        consignment_number=consignment_number,
        consignment_date=consignment_date,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=limit,
    )


router_tasks.add_api_route(
    path='',
    endpoint=get_tasks,
    summary="Gets tasks.",
    methods=['GET'],
)


@inject
async def add_products_to_consignment(
    products: list[AddProductModel],
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
):
    """Controller to add products to the consignment."""
    await service.add_products_to_consignment(
        products=products,
    )


router_tasks.add_api_route(
    path='/products',
    endpoint=add_products_to_consignment,
    summary="Adds products to consignments.",
    methods=['POST'],
)


@inject
async def get_task(
    task_id: int,
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
) -> Task:
    """Controller to get a task."""
    return await service.get_task(task_id=task_id)


router_tasks.add_api_route(
    path='/{task_id}',
    endpoint=get_task,
    summary="Gets a shift task by id.",
    methods=['GET'],
)


@inject
async def update_task(
    task_id: int,
    data: UpdateTaskModel,
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
) -> Task:
    """Controller to update a task."""
    return await service.update_task(task_id=task_id, data=data)


router_tasks.add_api_route(
    path='/{task_id}',
    endpoint=update_task,
    summary="Updates a shift task by id.",
    methods=['PUT'],
)


@inject
async def aggregate_products(
    consignment_id: int,
    product_id: str,
    service: TasksService = Depends(Provide[ServicesContainer.tasks_service]),
) -> None:
    """Controller to aggregate products."""
    return await service.aggregate_products(
        consignment_id=consignment_id,
        product_id=product_id,
    )


router_tasks.add_api_route(
    path='/products/{product_id}/consignments/{consignment_id}',
    endpoint=aggregate_products,
    summary="Aggregates products.",
    methods=['POST'],
)
