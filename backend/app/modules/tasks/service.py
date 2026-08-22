from datetime import datetime
from typing import Optional, Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.tasks.models import Task
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    async def create_task(
        session: AsyncSession,
        user_id: uuid.UUID,
        payload: TaskCreate,
    ) -> Task:
        repo = TaskRepository(session)
        return await repo.create_for_user(user_id=user_id, schema_in=payload)

    @staticmethod
    async def list_tasks(
        session: AsyncSession,
        user_id: uuid.UUID,
        *,
        is_completed: Optional[bool] = None,
        start_from: Optional[datetime] = None,
        end_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        repo = TaskRepository(session)
        return await repo.list_by_user(
            user_id=user_id,
            is_completed=is_completed,
            start_from=start_from,
            end_to=end_to,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def get_task(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Optional[Task]:
        repo = TaskRepository(session)
        return await repo.get_by_id_and_user(task_id=task_id, user_id=user_id)

    @staticmethod
    async def update_task(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        payload: TaskUpdate,
    ) -> Optional[Task]:
        repo = TaskRepository(session)
        task = await repo.get_by_id_and_user(task_id=task_id, user_id=user_id)
        if not task:
            return None
        return await repo.update_task(task=task, schema_in=payload)

    @staticmethod
    async def toggle_task_status(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        is_completed: Optional[bool] = None,
    ) -> Optional[Task]:
        repo = TaskRepository(session)
        task = await repo.get_by_id_and_user(task_id=task_id, user_id=user_id)
        if not task:
            return None

        new_status = is_completed if is_completed is not None else not task.is_completed
        return await repo.update_task(task=task, schema_in={"is_completed": new_status})

    @staticmethod
    async def delete_task(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> bool:
        repo = TaskRepository(session)
        task = await repo.get_by_id_and_user(task_id=task_id, user_id=user_id)
        if not task:
            return False
        await repo.delete_task(task)
        return True
