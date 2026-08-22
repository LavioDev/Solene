from datetime import datetime
from typing import Optional, Sequence
import uuid
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repository import BaseRepository
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Task, session=session)

    async def get_by_id_and_user(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        is_completed: Optional[bool] = None,
        start_from: Optional[datetime] = None,
        end_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        stmt = select(Task).where(Task.user_id == user_id)

        if is_completed is not None:
            stmt = stmt.where(Task.is_completed == is_completed)
        if start_from is not None:
            stmt = stmt.where(Task.start_time >= start_from)
        if end_to is not None:
            stmt = stmt.where(Task.end_time <= end_to)

        stmt = stmt.order_by(desc(Task.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_for_user(self, user_id: uuid.UUID, schema_in: TaskCreate) -> Task:
        data = schema_in.model_dump(exclude_unset=True)
        task = Task(user_id=user_id, **data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_task(self, task: Task, schema_in: TaskUpdate | dict) -> Task:
        return await self.update(db_obj=task, schema_in=schema_in)

    async def delete_task(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
