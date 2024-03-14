from datetime import date, datetime

from sqlalchemy import insert, select, cast, Date, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from src.db_models.tasks import Consignments, ShiftTasks, ProductsToConsignments
from src.modules.tasks.schemas import AddTaskModel, Task


class TasksRepository:

    def __init__(self):
        super().__init__()

    async def get_consignment(
        self,
        session: AsyncSession,
        consignment_number: int,
        consignment_date: date,
    ) -> int:
        """Gets the consignment by params."""
        stmt = (
            select(Consignments.consignment_id)
            .where(Consignments.consignment_number == consignment_number,
                   Consignments.consignment_date == consignment_date)
        )
        return (await session.execute(stmt)).scalar()

    async def add_consignment(
        self,
        session: AsyncSession,
        consignment_number: int,
        consignment_date: date,
    ) -> int:
        """Creates a new consignment."""
        stmt = (
            insert(Consignments)
            .values(consignment_number=consignment_number,
                    consignment_date=consignment_date)
            .returning(Consignments.consignment_id)
        )
        return (await session.execute(stmt)).scalar()

    async def add_task(
        self,
        session: AsyncSession,
        task: AddTaskModel,
        consignment_id: int,
    ):
        """Creates a new task."""
        stmt = (
            insert(ShiftTasks)
            .values(
                close_status=task.close_status,
                name=task.name,
                line=task.line,
                shift=task.shift,
                brigade=task.brigade,
                nomenclature=task.nomenclature,
                code=task.code,
                identifier=task.identifier,
                started_at=task.started_at,
                completed_at=task.completed_at,
                consignment_id=consignment_id,
                closed_at=None,
            )
        )
        await session.execute(stmt)

    async def get_tasks(
        self,
        session: AsyncSession,
        close_status: bool | None = None,
        consignment_number: int | None = None,
        consignment_date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        offset: int = 0,
        limit: int = 30,
    ):
        """Gets filtered tasks."""
        stmt = (
            select(ShiftTasks)
            .join(ShiftTasks.consignment)
            .join(Consignments.products, isouter=True)
            .options(contains_eager(ShiftTasks.consignment),
                     contains_eager(ShiftTasks.consignment).contains_eager(Consignments.products))
        )
        stmt = self.filter(
            stmt=stmt,
            close_status=close_status,
            consignment_number=consignment_number,
            consignment_date=consignment_date,
            start_date=start_date,
            end_date=end_date,
        )
        result = (await session.execute(stmt.offset(offset).limit(limit))).unique().scalars()
        return [Task.from_orm_task(task) for task in result]

    async def get_task(
        self,
        session: AsyncSession,
        task_id: int,
    ) -> Task | None:
        """Gets a task by ID."""
        stmt = (
            select(ShiftTasks)
            .join(ShiftTasks.consignment)
            .join(Consignments.products, isouter=True)
            .options(contains_eager(ShiftTasks.consignment),
                     contains_eager(ShiftTasks.consignment).contains_eager(Consignments.products))
            .where(ShiftTasks.task_id == task_id)
        )
        task = (await session.execute(stmt)).unique().scalar_one_or_none()
        return Task.from_orm_task(task) if task else None

    async def update_task(
        self,
        session: AsyncSession,
        task_id: int,
        data: dict,
        closed_at: datetime,
    ) -> Task | None:
        """Updates a task."""
        stmt = (
            update(ShiftTasks)
            .values(**data,
                    closed_at=closed_at)
            .where(ShiftTasks.task_id == task_id)
            .returning(ShiftTasks)
        )
        task = (await session.execute(stmt)).unique().scalar_one_or_none()
        if not task:
            return None
        return await self.get_task(session=session, task_id=task_id)

    def filter(
        self,
        stmt: select,
        close_status: bool | None = None,
        consignment_number: int | None = None,
        consignment_date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        """Filters tasks sql stmt."""
        filter_options = [
            (close_status, ShiftTasks.close_status),
            (consignment_number, Consignments.consignment_number),
            (consignment_date, Consignments.consignment_date),
        ]
        for option, column in filter_options:
            if option is not None:
                stmt = stmt.where(column == option)
        if start_date:
            stmt = stmt.where(cast(ShiftTasks.started_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(ShiftTasks.completed_at, Date) <= end_date)
        return stmt

    async def add_products_to_consignment(
        self,
        session: AsyncSession,
        consignment_id: int,
        product_id: str,
    ) -> int:
        """Binds a product to a consignment."""
        stmt = (
            insert(ProductsToConsignments)
            .values(consignment_id=consignment_id,
                    product_id=product_id,
                    is_aggregated=True,
                    aggregated_at=datetime.now())
            .returning(ProductsToConsignments.product_to_consignment_id)
        )
        return (await session.execute(stmt)).scalar()

    async def get_product_to_consignment(
        self,
        session: AsyncSession,
        consignment_id: int,
        product_id: str,
    ) -> bool | None:
        """Gets data from ProductsToConsignments table by product and consignment IDs."""
        stmt = (
            select(ProductsToConsignments.is_aggregated)
            .where(ProductsToConsignments.product_id == product_id,
                   ProductsToConsignments.consignment_id == consignment_id)
        )
        return (await session.execute(stmt)).scalar()

    async def get_consignments_by_product(
        self,
        session: AsyncSession,
        product_id: str,
    ) -> list[int] | None:
        """Gets a consignment from ProductsToConsignments by product ID."""
        stmt = (
            select(ProductsToConsignments.consignment_id)
            .where(ProductsToConsignments.product_id == product_id)
        )
        return list((await session.execute(stmt)).scalars())

    async def aggregate(
        self,
        session: AsyncSession,
        consignment_id: int,
        product_id: str,
    ) -> None:
        """Aggregates products."""
        stmt = (
            update(ProductsToConsignments)
            .values(is_aggregated=True,
                    aggregated_at=datetime.now())
            .where(ProductsToConsignments.product_id == product_id,
                   ProductsToConsignments.consignment_id == consignment_id)
            .returning(ProductsToConsignments.product_to_consignment_id)
        )
        await session.execute(stmt)
