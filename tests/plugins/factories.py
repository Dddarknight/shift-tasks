from datetime import datetime
from uuid import uuid4

import pytest
from mimesis import Field, Locale

from src.db_models.products import Products
from src.db_models.tasks import ShiftTasks, Consignments, ProductsToConsignments


@pytest.fixture()
def db_consignments_factory(
    insert_query_factory,
    generate_schema,
):
    async def factory(**overriders):
        _ = Field(locale=Locale.RU)
        schema = generate_schema({
            "consignment_number": _("integer_number"),
            "consignment_date":  datetime.now().date(),
        })
        return await insert_query_factory(
            Consignments(**{**schema, **overriders}),
        )

    return factory


@pytest.fixture()
async def generic_consignment(db_consignments_factory):
    return await db_consignments_factory()


@pytest.fixture()
def db_tasks_factory(
    insert_query_factory,
    generate_schema,
    generic_consignment,
):
    async def factory(**overriders):
        schema = generate_schema({
            'name': str(uuid4()),
            'line': str(uuid4()),
            'shift': str(uuid4()),
            'brigade': str(uuid4()),
            'consignment_id': generic_consignment.consignment_id,
            'nomenclature': str(uuid4()),
            'code': str(uuid4()),
            'identifier': str(uuid4()),
            'started_at': datetime.now().replace(hour=8, minute=0, second=0),
            'completed_at': datetime.now().replace(hour=16, minute=0, second=0),
            'closed_at': None,
            'close_status': False,
        })
        return await insert_query_factory(
            ShiftTasks(**{**schema, **overriders}),
        )

    return factory


@pytest.fixture()
async def generic_task(db_tasks_factory):
    return await db_tasks_factory()


@pytest.fixture()
def db_products_factory(
    insert_query_factory,
    generate_schema,
):
    async def factory(**overriders):
        _ = Field(locale=Locale.RU)
        schema = generate_schema({
            "product_id":  str(uuid4()),
        })
        return await insert_query_factory(
            Products(**{**schema, **overriders}),
        )

    return factory


@pytest.fixture()
async def generic_product(db_products_factory):
    return await db_products_factory()


@pytest.fixture()
def db_product_to_consignment_factory(
    insert_query_factory,
    generate_schema,
    generic_consignment,
    generic_product,
):
    async def factory(**overriders):
        _ = Field(locale=Locale.RU)
        schema = generate_schema({
            "product_id":  generic_product.product_id,
            "consignment_id": generic_consignment.consignment_id,
        })
        return await insert_query_factory(
            ProductsToConsignments(**{**schema, **overriders}),
        )

    return factory


@pytest.fixture()
async def generic_product_to_consignment(db_product_to_consignment_factory):
    return await db_product_to_consignment_factory()
