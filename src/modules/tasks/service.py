from datetime import date, datetime

from src.adapters.database import AsyncSessionManager
from src.base_service import BaseService
from src.modules.exceptions import HTTPNotFoundError, HTTPBadRequestError
from src.modules.tasks.repository import TasksRepository
from src.modules.tasks.schemas import AddTaskModel, Task, AddProductModel, UpdateTaskModel


class TasksService(BaseService):

    def __init__(
        self,
        *,
        session_factory: AsyncSessionManager,
        tasks_repository: TasksRepository,
    ):
        super().__init__(session_factory)
        self.tasks_repository = tasks_repository

    async def add_task(self, tasks: list[AddTaskModel]):
        """Creates a new task. Checks if the consignment exists and creates it if not."""
        async with self.session_factory() as session:
            for task in tasks:
                consignment_id = await self.tasks_repository.get_consignment(
                    session=session,
                    consignment_number=task.consignment_number,
                    consignment_date=task.consignment_date,
                )
                if not consignment_id:
                    consignment_id = await self.tasks_repository.add_consignment(
                        session=session,
                        consignment_number=task.consignment_number,
                        consignment_date=task.consignment_date,
                    )
                await self.tasks_repository.add_task(
                    session=session, task=task, consignment_id=consignment_id)

    async def get_tasks(
        self,
        close_status: bool | None = None,
        consignment_number: int | None = None,
        consignment_date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        offset: int = 0,
        limit: int = 30,
    ) -> list[Task]:
        """Gets filtered tasks."""
        async with self.session_factory() as session:
            return await self.tasks_repository.get_tasks(
                session=session,
                close_status=close_status,
                consignment_number=consignment_number,
                consignment_date=consignment_date,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                limit=limit,
            )

    async def get_task(
        self,
        task_id: int,
    ) -> Task:
        """Gets a task by ID."""
        async with self.session_factory() as session:
            task = await self.tasks_repository.get_task(
                session=session,
                task_id=task_id,
            )
            if not task:
                raise HTTPNotFoundError
            return task

    async def update_task(
        self,
        task_id: int,
        data: UpdateTaskModel,
    ) -> Task:
        """Updates a task. Checks given data and deletes fields that are not changed."""
        async with self.session_factory() as session:
            closed_at = None
            if data.close_status is True:
                closed_at = datetime.now()
            data_to_update = {
                key: value
                for key, value in data.model_dump().items()
                if value is not None
            }
            task = await self.tasks_repository.update_task(
                session=session,
                task_id=task_id,
                data=data_to_update,
                closed_at=closed_at,
            )
            if not task:
                raise HTTPNotFoundError
            return task

    async def add_products_to_consignment(
        self,
        products: list[AddProductModel],
    ):
        """Binds products to the consignment."""
        async with self.session_factory() as session:
            for product in products:
                consignment_id = await self.tasks_repository.get_consignment(
                    session=session,
                    consignment_number=product.consignment_number,
                    consignment_date=product.consignment_date,
                )
                if not consignment_id:
                    continue
                await self.tasks_repository.add_products_to_consignment(
                    session=session,
                    consignment_id=consignment_id,
                    product_id=product.product_id,
                )

    async def aggregate_products(
        self,
        consignment_id: int,
        product_id: str,
    ) -> None:
        """Aggregates products within given consignment.
                Raises errors if the products were already aggregated,
                if the products are binded to another consignment
                and if the consignment for the products are not found."""
        async with self.session_factory() as session:
            is_aggregated = (
                await self.tasks_repository.get_product_to_consignment(
                    session=session,
                    consignment_id=consignment_id,
                    product_id=product_id,
                )
            )
            if is_aggregated is True:
                raise HTTPBadRequestError(detail="unique code already used at {aggregated_at}")
            if is_aggregated is None:
                consignments = await self.tasks_repository.get_consignments_by_product(
                    session=session,
                    product_id=product_id,
                )
                if consignments:
                    raise HTTPBadRequestError(detail="unique code is attached to another batch")
                raise HTTPNotFoundError
            await self.tasks_repository.aggregate(
                session=session,
                consignment_id=consignment_id,
                product_id=product_id,
            )
