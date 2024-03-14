from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select

from src.db_models.tasks import ProductsToConsignments, Consignments, ShiftTasks
from src.modules.tasks.schemas import Task


@pytest.fixture()
def assert_task(
    generic_task,
    generic_consignment,
    generic_product_to_consignment,
):
    def check(task):
        expected = Task(
            close_status=generic_task.close_status,
            name=generic_task.name,
            line=generic_task.line,
            shift=generic_task.shift,
            brigade=generic_task.brigade,
            consignment_number=generic_consignment.consignment_number,
            consignment_date=generic_consignment.consignment_date,
            nomenclature=generic_task.nomenclature,
            code=generic_task.code,
            identifier=generic_task.identifier,
            started_at=generic_task.started_at,
            completed_at=generic_task.completed_at,
            closed_at=generic_task.closed_at,
            products=[generic_product_to_consignment.product_id]
        )
        assert task == expected
    return check


@pytest_asyncio.fixture()
async def assert_aggregation(
    test_session,
    generic_product_to_consignment,
):
    async def inner():
        stmt = (
            select(ProductsToConsignments.is_aggregated,
                   ProductsToConsignments.aggregated_at)
            .where(ProductsToConsignments.product_id == generic_product_to_consignment.product_id,
                   ProductsToConsignments.consignment_id == generic_product_to_consignment.consignment_id)
        )
        data = (await test_session.execute(stmt)).one_or_none()
        assert data.is_aggregated is True
        assert data.aggregated_at is not None
    return inner


@pytest.fixture()
def task_data():
    return {
        "СтатусЗакрытия": False,
        "ПредставлениеЗаданияНаСмену": "Задание на смену 2345",
        "Рабочий центр": "Т2",
        "Смена": "1",
        "Бригада": "Бригада №4",
        "НомерПартии": 22222,
        "ДатаПартии": "2024-01-30",
        "Номенклатура": "Какая то номенклатура",
        "КодЕКН": "456678",
        "ИдентификаторРЦ": "A",
        "ДатаВремяНачалаСмены": "2024-01-30T20:00:00+05:00",
        "ДатаВремяОкончанияСмены": "2024-01-31T08:00:00+05:00"
    }


@pytest_asyncio.fixture()
async def assert_created_task(task_data, test_session):
    async def check():
        stmt = (
            select(Consignments.consignment_number,
                   Consignments.consignment_date)
        )
        data = (await test_session.execute(stmt)).one_or_none()
        assert data.consignment_number == task_data['НомерПартии']
        assert data.consignment_date == datetime.strptime(task_data['ДатаПартии'], "%Y-%m-%d").date()
        stmt = (
            select(ShiftTasks.shift,
                   ShiftTasks.close_status,
                   ShiftTasks.started_at,
                   ShiftTasks.completed_at,
                   ShiftTasks.identifier,
                   ShiftTasks.code,
                   ShiftTasks.nomenclature,
                   ShiftTasks.brigade)
        )
        data = (await test_session.execute(stmt)).one_or_none()
        assert data.shift == task_data['Смена']
        assert data.close_status == task_data['СтатусЗакрытия']
        assert data.started_at == datetime.fromisoformat(
            task_data['ДатаВремяНачалаСмены']).replace(tzinfo=None)
        assert data.completed_at == datetime.fromisoformat(
            task_data['ДатаВремяОкончанияСмены']).replace(tzinfo=None)
        assert data.identifier == task_data['ИдентификаторРЦ']
        assert data.code == task_data['КодЕКН']
        assert data.nomenclature == task_data['Номенклатура']
        assert data.brigade == task_data['Бригада']
    return check
