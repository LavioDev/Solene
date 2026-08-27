from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional, Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.couples.models import Couple, CoupleInvitation
from app.modules.couples.repository import CoupleRepository
from app.modules.couples.schemas import (
    CoupleCreate,
    CoupleInvitationAcceptPayload,
    CoupleInvitationCreateResponse,
    CoupleInvitationInfoResponse,
    CoupleOut,
    CoupleUpdate,
    UserPartnerSummary,
)


INVITATION_CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


class CoupleService:
    @staticmethod
    def _generate_code(length: int = 6) -> str:
        random_str = "".join(secrets.choice(INVITATION_CHARS) for _ in range(length))
        return f"SL-{random_str}"

    @staticmethod
    async def create_invitation(
        session: AsyncSession,
        current_user_id: uuid.UUID,
    ) -> CoupleInvitationCreateResponse:
        repo = CoupleRepository(session)
        # Check if current user is already in an active couple
        existing_couple = await repo.get_by_user_id(user_id=current_user_id, status="active")
        if existing_couple:
            raise ConflictException("You are already in an active couple relationship.")

        # Generate a unique code
        code = CoupleService._generate_code()
        for _ in range(5):
            existing_inv = await repo.get_invitation_by_code(code)
            if not existing_inv:
                break
            code = CoupleService._generate_code()

        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        invitation = await repo.create_invitation(
            inviter_id=current_user_id,
            code=code,
            expires_at=expires_at,
        )

        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(current_user_id)
        inviter_summary = UserPartnerSummary.model_validate(user) if user else None

        return CoupleInvitationCreateResponse(
            id=invitation.id,
            inviter_id=invitation.inviter_id,
            code=invitation.code,
            status=invitation.status,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            invite_url=f"/pair?code={invitation.code}",
            inviter=inviter_summary,
        )

    @staticmethod
    async def get_current_invitation(
        session: AsyncSession,
        current_user_id: uuid.UUID,
    ) -> Optional[CoupleInvitationCreateResponse]:
        repo = CoupleRepository(session)
        invitation = await repo.get_active_invitation_by_inviter(current_user_id)
        if not invitation:
            return None

        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(current_user_id)
        inviter_summary = UserPartnerSummary.model_validate(user) if user else None

        return CoupleInvitationCreateResponse(
            id=invitation.id,
            inviter_id=invitation.inviter_id,
            code=invitation.code,
            status=invitation.status,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            invite_url=f"/pair?code={invitation.code}",
            inviter=inviter_summary,
        )

    @staticmethod
    async def revoke_current_invitation(
        session: AsyncSession,
        current_user_id: uuid.UUID,
    ) -> bool:
        repo = CoupleRepository(session)
        invitation = await repo.get_active_invitation_by_inviter(current_user_id)
        if not invitation:
            return False
        await repo.revoke_invitation(invitation)
        return True

    @staticmethod
    async def get_invitation_info(
        session: AsyncSession,
        code: str,
        current_user_id: Optional[uuid.UUID] = None,
    ) -> CoupleInvitationInfoResponse:
        repo = CoupleRepository(session)
        invitation = await repo.get_invitation_by_code(code.strip().upper())
        now = datetime.now(timezone.utc)

        if not invitation:
            return CoupleInvitationInfoResponse(
                code=code,
                status="not_found",
                is_valid=False,
                expires_at=now,
                inviter=None,
                error_reason="Invitation code does not exist.",
            )

        if invitation.status != "pending" or invitation.expires_at <= now:
            return CoupleInvitationInfoResponse(
                code=code,
                status="expired" if invitation.expires_at <= now else invitation.status,
                is_valid=False,
                expires_at=invitation.expires_at,
                inviter=None,
                error_reason="Invitation link has expired or has already been used.",
            )

        # Check if inviter is already in an active couple
        inviter_couple = await repo.get_by_user_id(user_id=invitation.inviter_id, status="active")
        if inviter_couple:
            return CoupleInvitationInfoResponse(
                code=code,
                status="invalid",
                is_valid=False,
                expires_at=invitation.expires_at,
                inviter=None,
                error_reason="The person who created this invitation is already paired in another relationship.",
            )

        inviter_summary = (
            UserPartnerSummary.model_validate(invitation.inviter) if invitation.inviter else None
        )

        return CoupleInvitationInfoResponse(
            code=invitation.code,
            status=invitation.status,
            is_valid=True,
            expires_at=invitation.expires_at,
            inviter=inviter_summary,
            error_reason=None,
        )

    @staticmethod
    async def accept_invitation(
        session: AsyncSession,
        current_user_id: uuid.UUID,
        payload: CoupleInvitationAcceptPayload,
    ) -> CoupleOut:
        repo = CoupleRepository(session)
        code = payload.code.strip().upper()
        now = datetime.now(timezone.utc)

        # Check if current user is already in active relationship
        my_existing_couple = await repo.get_by_user_id(user_id=current_user_id, status="active")
        if my_existing_couple:
            raise ConflictException("You are already in an active couple relationship.")

        invitation = await repo.get_invitation_by_code(code)
        if not invitation:
            raise NotFoundException("Invitation code does not exist.")

        if invitation.status != "pending":
            raise BadRequestException(f"Invitation is no longer valid (status: {invitation.status}).")

        if invitation.expires_at <= now:
            raise BadRequestException("Invitation code has expired.")

        if invitation.inviter_id == current_user_id:
            raise BadRequestException("You cannot accept your own couple invitation.")

        inviter_couple = await repo.get_by_user_id(user_id=invitation.inviter_id, status="active")
        if inviter_couple:
            raise ConflictException("The inviter is already in an active couple relationship.")

        couple = await repo.accept_invitation_and_create_couple(
            invitation=invitation,
            partner_id=current_user_id,
            start_date=payload.start_date,
            nickname=payload.nickname,
            cover_url=payload.cover_url,
        )
        return CoupleOut.model_validate(couple)

    @staticmethod
    async def create_couple(
        session: AsyncSession,
        current_user_id: uuid.UUID,
        payload: CoupleCreate,
        actor: Optional[User] = None,
    ) -> Couple:
        user_repo = UserRepository(session)
        is_management = actor and (actor.role in ["admin", "manager"])
        user1_id = payload.user1_id if (payload.user1_id and is_management) else (payload.user1_id or current_user_id)
        user2_id = payload.user2_id

        if user1_id == user2_id:
            raise BadRequestException("Cannot create a couple with yourself.")

        # Validate partner existence
        partner = await user_repo.get_by_id(user2_id)
        if not partner:
            raise NotFoundException("Partner user not found.")

        # Validate primary user existence
        user1 = await user_repo.get_by_id(user1_id)
        if not user1:
            raise NotFoundException("Primary user not found.")

        repo = CoupleRepository(session)
        return await repo.create_couple(user1_id=user1_id, schema_in=payload)

    @staticmethod
    async def get_my_couple(
        session: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        return await repo.get_by_user_id(user_id=user_id, status=status)

    @staticmethod
    async def get_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        actor: Optional[User] = None,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        is_management = actor and (actor.role in ["admin", "manager"])
        if is_management:
            return await repo.get_by_id_with_users(couple_id)
        return await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)

    @staticmethod
    async def list_couples(
        session: AsyncSession,
        user_id: uuid.UUID,
        actor: Optional[User] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> tuple[Sequence[Couple], int]:
        repo = CoupleRepository(session)
        actual_skip = skip if skip is not None else max(0, (page - 1) * per_page)
        actual_limit = limit if limit is not None else per_page
        is_management = actor and (actor.role in ["admin", "manager"])
        if is_management:
            items = await repo.list_all(status=status, skip=actual_skip, limit=actual_limit)
            total = await repo.count_all(status=status)
        else:
            items = await repo.list_for_user(user_id=user_id, status=status, skip=actual_skip, limit=actual_limit)
            total = await repo.count_for_user(user_id=user_id, status=status)
        return items, total

    @staticmethod
    async def update_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: CoupleUpdate,
        actor: Optional[User] = None,
    ) -> Optional[Couple]:
        repo = CoupleRepository(session)
        is_management = actor and (actor.role in ["admin", "manager"])
        couple = await repo.get_by_id_with_users(couple_id) if is_management else await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)
        if not couple:
            return None

        return await repo.update_couple(couple=couple, schema_in=payload)

    @staticmethod
    async def delete_couple(
        session: AsyncSession,
        couple_id: uuid.UUID,
        user_id: uuid.UUID,
        actor: Optional[User] = None,
    ) -> bool:
        # Invariant Guard: Manager CANNOT delete couples
        if actor and actor.role == "manager":
            raise ForbiddenException("Managers do not have permission to delete couple records.")

        repo = CoupleRepository(session)
        is_admin = actor and actor.role == "admin"
        couple = await repo.get_by_id_with_users(couple_id) if is_admin else await repo.get_couple_for_user(couple_id=couple_id, user_id=user_id)
        if not couple:
            return False

        await repo.delete_couple(couple)
        return True

