from datetime import timedelta, datetime

import pytest


@pytest.mark.parametrize(
    'params',
    [{'close_status': False},
     {'start_date': datetime.now() - timedelta(days=1)},
     {'end_date': datetime.now() + timedelta(days=1)}],
)
@pytest.mark.asyncio()
async def test_get_tasks(
    tasks_repository,
    test_session,
    params,
    assert_task,
):
    """Tests getting tasks data."""
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    tasks_data = await tasks_repository.get_tasks(
        test_session,
        close_status=params.get('close_status'),
        start_date=start_date.replace(tzinfo=None) if start_date else None,
        end_date=end_date.replace(tzinfo=None) if end_date else None,
    )
    task = tasks_data[0]
    assert_task(task)


@pytest.mark.parametrize(
    'params',
    [{'close_status': True},
     {'start_date': datetime.now() + timedelta(days=1)},
     {'end_date': datetime.now() - timedelta(days=1)}],
)
@pytest.mark.asyncio()
async def test_get_no_tasks(
    tasks_repository,
    test_session,
    params,
):
    """Tests getting no tasks with invalid params."""
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    tasks_data = await tasks_repository.get_tasks(
        test_session,
        close_status=params.get('close_status'),
        start_date=start_date.replace(tzinfo=None) if start_date else None,
        end_date=end_date.replace(tzinfo=None) if end_date else None,
    )
    assert tasks_data == []


@pytest.mark.asyncio()
async def test_get_task(
    tasks_repository,
    test_session,
    generic_task,
    assert_task,
):
    """Tests getting a task by ID."""
    task = await tasks_repository.get_task(
        test_session,
        task_id=generic_task.task_id
    )
    assert_task(task)
