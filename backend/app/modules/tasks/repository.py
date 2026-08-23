from datetime import datetime
from typing import Optional, Sequence
import uuid
from sqlalchemy import desc, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repository import BaseRepository
from app.modules.couples.models import Couple
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Task, session=session)

    async def get_by_id_and_user(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
        couple_stmt = (
            select(Couple)
            .where(
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
                Couple.status == "active",
            )
            .order_by(desc(Couple.created_at))
        )
        couple_res = await self.session.execute(couple_stmt)
        couple = couple_res.scalars().first()
        partner_id = None
        if couple:
            partner_id = couple.user2_id if couple.user1_id == user_id else couple.user1_id

        if partner_id:
            user_filter = or_(
                Task.user_id == user_id,
                and_(Task.user_id == partner_id, Task.is_shared == True),
            )
        else:
            user_filter = (Task.user_id == user_id)

        stmt = select(Task).where(Task.id == task_id, user_filter)
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
        couple_stmt = (
            select(Couple)
            .where(
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
                Couple.status == "active",
            )
            .order_by(desc(Couple.created_at))
        )
        couple_res = await self.session.execute(couple_stmt)
        couple = couple_res.scalars().first()
        partner_id = None
        if couple:
            partner_id = couple.user2_id if couple.user1_id == user_id else couple.user1_id

        if partner_id:
            user_filter = or_(
                Task.user_id == user_id,
                and_(Task.user_id == partner_id, Task.is_shared == True),
            )
        else:
            user_filter = (Task.user_id == user_id)

        stmt = select(Task).where(user_filter)

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

    async def get_current_active_task_for_user(self, user_id: uuid.UUID, now: datetime) -> Optional[Task]:
        from sqlalchemy import case, or_
        priority_order = case(
            {
                "urgent": 1,
                "high": 2,
                "medium": 3,
                "low": 4,
            },
            value=Task.priority,
            else_=5,
        )
        stmt = (
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.start_time.is_not(None),
                Task.start_time <= now,
                or_(Task.end_time.is_(None), Task.end_time >= now),
            )
            .order_by(priority_order, Task.start_time.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

