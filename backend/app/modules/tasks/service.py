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

    @staticmethod
    async def get_partner_active_status(
        session: AsyncSession,
        user_id: uuid.UUID,
    ):
        from datetime import timezone
        from app.modules.couples.repository import CoupleRepository
        from app.modules.couples.schemas import UserPartnerSummary
        from app.modules.tasks.schemas import PartnerActiveStatusOut, TaskOut

        couple_repo = CoupleRepository(session)
        couple = await couple_repo.get_by_user_id(user_id=user_id, status="active")
        if not couple:
            return PartnerActiveStatusOut(in_couple=False, is_busy=False)

        partner_obj = couple.user2 if couple.user1_id == user_id else couple.user1
        if not partner_obj:
            return PartnerActiveStatusOut(in_couple=True, partner=None, is_busy=False)

        partner_summary = UserPartnerSummary.model_validate(partner_obj)
        now = datetime.now(timezone.utc)
        task_repo = TaskRepository(session)
        active_task = await task_repo.get_current_active_task_for_user(user_id=partner_obj.id, now=now)

        if active_task:
            return PartnerActiveStatusOut(
                in_couple=True,
                partner=partner_summary,
                is_busy=True,
                active_task=TaskOut.model_validate(active_task),
            )

        return PartnerActiveStatusOut(
            in_couple=True,
            partner=partner_summary,
            is_busy=False,
            active_task=None,
        )

