from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_, and_
from sqlalchemy.orm import selectinload
from app.modules.couples.models import Couple
from app.modules.notes.models import UserNote, NoteImage
from app.modules.notes.schemas import NoteCreate, NoteUpdate


class NoteService:
    @staticmethod
    async def create_note(session: AsyncSession, user_id: UUID, payload: NoteCreate) -> UserNote:
        # Determine primary image_url if image_urls provided
        primary_image_url = payload.image_url
        if payload.image_urls and len(payload.image_urls) > 0:
            primary_image_url = payload.image_urls[0]

        note = UserNote(
            user_id=user_id,
            title=payload.title,
            content=payload.content,
            image_url=primary_image_url,
            category=payload.category,
            display_type=payload.display_type,
            target_date=payload.target_date,
            is_shared=payload.is_shared,
        )

        # Attach NoteImage records if image_urls provided
        if payload.image_urls:
            for url in payload.image_urls:
                if url and url.strip():
                    img = NoteImage(file_path=url.strip())
                    note.images.append(img)
        elif payload.image_url:
            img = NoteImage(file_path=payload.image_url.strip())
            note.images.append(img)

        session.add(note)
        await session.commit()
        await session.refresh(note)
        return note

    @staticmethod
    async def list_user_notes(
        session: AsyncSession,
        user_id: UUID,
        page: int = 1,
        per_page: int = 15,
        display_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[UserNote], int]:
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
                UserNote.user_id == user_id,
                and_(UserNote.user_id == partner_id, UserNote.is_shared == True),
            )
        else:
            user_filter = (UserNote.user_id == user_id)

        base_stmt = select(UserNote).where(user_filter)

        if display_type and display_type.upper() in ["DATE", "RANDOM"]:
            base_stmt = base_stmt.where(UserNote.display_type == display_type.upper())

        if search and search.strip():
            term = f"%{search.strip()}%"
            base_stmt = base_stmt.where(
                (UserNote.title.ilike(term)) | (UserNote.content.ilike(term))
            )

        # Count total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one()

        # Paginated items
        offset = max(0, (page - 1) * per_page)
        stmt = (
            base_stmt
            .options(selectinload(UserNote.images))
            .order_by(desc(UserNote.created_at))
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def update_note(session: AsyncSession, user_id: UUID, note_id: UUID, payload: NoteUpdate) -> Optional[UserNote]:
        stmt = (
            select(UserNote)
            .where(UserNote.id == note_id, UserNote.user_id == user_id)
            .options(selectinload(UserNote.images))
        )
        result = await session.execute(stmt)
        note = result.scalars().first()
        if not note:
            return None

        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content
        if payload.category is not None:
            note.category = payload.category
        if payload.display_type is not None:
            note.display_type = payload.display_type
        if payload.target_date is not None:
            note.target_date = payload.target_date
        if payload.is_shared is not None:
            note.is_shared = payload.is_shared

        if payload.image_urls is not None:
            # Replace images
            note.images.clear()
            for url in payload.image_urls:
                if url and url.strip():
                    note.images.append(NoteImage(file_path=url.strip()))
            note.image_url = payload.image_urls[0] if payload.image_urls else None
        elif payload.image_url is not None:
            note.image_url = payload.image_url
            if not note.images and payload.image_url:
                note.images.append(NoteImage(file_path=payload.image_url.strip()))

        await session.commit()
        await session.refresh(note)
        return note

    @staticmethod
    async def delete_note(session: AsyncSession, user_id: UUID, note_id: UUID) -> bool:
        stmt = select(UserNote).where(UserNote.id == note_id, UserNote.user_id == user_id)
        result = await session.execute(stmt)
        note = result.scalars().first()
        if not note:
            return False
        await session.delete(note)
        await session.commit()
        return True
