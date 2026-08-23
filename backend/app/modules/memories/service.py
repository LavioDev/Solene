from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_, and_
from sqlalchemy.orm import selectinload
from app.modules.couples.models import Couple
from app.modules.memories.models import Memory, MemoryImage
from app.modules.memories.schemas import MemoryCreate, MemoryUpdate


class MemoryService:
    @staticmethod
    async def create_memory(session: AsyncSession, user_id: UUID, payload: MemoryCreate) -> Memory:
        primary_image_url = payload.image_url
        if payload.image_urls and len(payload.image_urls) > 0:
            primary_image_url = payload.image_urls[0]

        memory = Memory(
            user_id=user_id,
            title=payload.title,
            content=payload.content,
            image_url=primary_image_url,
            category=payload.category,
            display_type=payload.display_type,
            target_date=payload.target_date,
            is_shared=payload.is_shared,
        )

        if payload.image_urls:
            for url in payload.image_urls:
                if url and url.strip():
                    img = MemoryImage(file_path=url.strip())
                    memory.images.append(img)
        elif payload.image_url:
            img = MemoryImage(file_path=payload.image_url.strip())
            memory.images.append(img)

        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        return memory

    @staticmethod
    async def list_user_memories(
        session: AsyncSession,
        user_id: UUID,
        page: int = 1,
        per_page: int = 15,
        display_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Memory], int]:
        couple_stmt = (
            select(Couple)
            .where(
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
                Couple.status == "active",
            )
            .order_by(desc(Couple.created_at))
        )
        couple_res = await session.execute(couple_stmt)
        couple = couple_res.scalars().first()
        partner_id = None
        if couple:
            partner_id = couple.user2_id if couple.user1_id == user_id else couple.user1_id

        if partner_id:
            user_filter = or_(
                Memory.user_id == user_id,
                and_(Memory.user_id == partner_id, Memory.is_shared == True),
            )
        else:
            user_filter = (Memory.user_id == user_id)

        base_stmt = select(Memory).where(user_filter)

        if display_type and display_type.upper() in ["DATE", "RANDOM"]:
            base_stmt = base_stmt.where(Memory.display_type == display_type.upper())

        if search and search.strip():
            term = f"%{search.strip()}%"
            base_stmt = base_stmt.where(
                (Memory.title.ilike(term)) | (Memory.content.ilike(term))
            )

        # Count total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one()

        # Paginated items
        offset = max(0, (page - 1) * per_page)
        stmt = (
            base_stmt
            .options(selectinload(Memory.images))
            .order_by(desc(Memory.created_at))
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def update_memory(
        session: AsyncSession, user_id: UUID, memory_id: UUID, payload: MemoryUpdate
    ) -> Optional[Memory]:
        stmt = (
            select(Memory)
            .where(Memory.id == memory_id, Memory.user_id == user_id)
            .options(selectinload(Memory.images))
        )
        result = await session.execute(stmt)
        memory = result.scalars().first()
        if not memory:
            return None

        if payload.title is not None:
            memory.title = payload.title
        if payload.content is not None:
            memory.content = payload.content
        if payload.category is not None:
            memory.category = payload.category
        if payload.display_type is not None:
            memory.display_type = payload.display_type
        if payload.target_date is not None:
            memory.target_date = payload.target_date
        if payload.is_shared is not None:
            memory.is_shared = payload.is_shared

        if payload.image_urls is not None:
            memory.images.clear()
            for url in payload.image_urls:
                if url and url.strip():
                    memory.images.append(MemoryImage(file_path=url.strip()))
            memory.image_url = payload.image_urls[0] if payload.image_urls else None
        elif payload.image_url is not None:
            memory.image_url = payload.image_url
            if not memory.images and payload.image_url:
                memory.images.append(MemoryImage(file_path=payload.image_url.strip()))

        await session.commit()
        await session.refresh(memory)
        return memory

    @staticmethod
    async def delete_memory(session: AsyncSession, user_id: UUID, memory_id: UUID) -> bool:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await session.execute(stmt)
        memory = result.scalars().first()
        if not memory:
            return False
        await session.delete(memory)
        await session.commit()
        return True
