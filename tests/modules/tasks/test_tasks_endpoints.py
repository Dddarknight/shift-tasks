import pytest


@pytest.mark.asyncio
async def test_endpoint_aggregate(
    async_client,
    test_session,
    test_app,
    tasks_service,
    generic_product_to_consignment,
    assert_aggregation,
):
    """Tests aggregate endpoint."""
    with test_app.services_container.tasks_service.override(tasks_service):
        product_id = generic_product_to_consignment.product_id
        consignment_id = generic_product_to_consignment.consignment_id
        response = await async_client.post(
            f'/v1/tasks/products/{product_id}/consignments/{consignment_id}',
        )
        assert response.status_code == 200
        await assert_aggregation()


@pytest.mark.asyncio
async def test_endpoint_aggregate_invalid_product(
    async_client,
    test_session,
    test_app,
    tasks_service,
    generic_product_to_consignment,
    assert_aggregation,
):
    """Tests aggregate endpoint errors."""
    with test_app.services_container.tasks_service.override(tasks_service):
        product_id = generic_product_to_consignment.product_id + '1'
        consignment_id = generic_product_to_consignment.consignment_id
        response = await async_client.post(
            f'/v1/tasks/products/{product_id}/consignments/{consignment_id}',
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_aggregate_invalid_consignment(
    async_client,
    test_session,
    test_app,
    tasks_service,
    generic_product_to_consignment,
    assert_aggregation,
):
    """Tests aggregate endpoint with invalid consignment."""
    with test_app.services_container.tasks_service.override(tasks_service):
        product_id = generic_product_to_consignment.product_id
        consignment_id = generic_product_to_consignment.consignment_id + 1
        response = await async_client.post(
            f'/v1/tasks/products/{product_id}/consignments/{consignment_id}',
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_endpoint_aggregate_already_aggregated(
    async_client,
    test_session,
    test_app,
    tasks_service,
    generic_product_to_consignment,
    assert_aggregation,
):
    """Tests aggregate endpoint if the products were already aggregated."""
    with test_app.services_container.tasks_service.override(tasks_service):
        product_id = generic_product_to_consignment.product_id
        consignment_id = generic_product_to_consignment.consignment_id
        generic_product_to_consignment.is_aggregated = True
        response = await async_client.post(
            f'/v1/tasks/products/{product_id}/consignments/{consignment_id}',
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_endpoint_create_task(
    async_client,
    test_session,
    test_app,
    tasks_service,
    task_data,
    assert_created_task,
):
    """Tests task creation."""
    with test_app.services_container.tasks_service.override(tasks_service):
        response = await async_client.post(
            '/v1/tasks',
            json=[task_data]
        )
        assert response.status_code == 200
        await assert_created_task()
