"""add_couple_invitations_table

Revision ID: 0003_add_couple_invitations
Revises: 0002_add_permissions
Create Date: 2026-08-26 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_add_couple_invitations'
down_revision: Union[str, None] = '0002_add_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'couple_invitations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('inviter_id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_couple_invitations_code'), 'couple_invitations', ['code'], unique=True)
    op.create_index(op.f('ix_couple_invitations_inviter_id'), 'couple_invitations', ['inviter_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_couple_invitations_inviter_id'), table_name='couple_invitations')
    op.drop_index(op.f('ix_couple_invitations_code'), table_name='couple_invitations')
    op.drop_table('couple_invitations')
