from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
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
    async def list_user_notes(session: AsyncSession, user_id: UUID) -> List[UserNote]:
        stmt = (
            select(UserNote)
            .where(UserNote.user_id == user_id)
            .options(selectinload(UserNote.images))
            .order_by(desc(UserNote.created_at))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

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
