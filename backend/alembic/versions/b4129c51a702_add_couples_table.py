"""add_couples_table

Revision ID: b4129c51a702
Revises: f3178a9c2d10
Create Date: 2026-08-22 20:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4129c51a702'
down_revision: Union[str, None] = 'f3178a9c2d10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'couples',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user1_id', sa.UUID(), nullable=False),
        sa.Column('user2_id', sa.UUID(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('nickname', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('cover_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_couples_user1_id'), 'couples', ['user1_id'], unique=False)
    op.create_index(op.f('ix_couples_user2_id'), 'couples', ['user2_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_couples_user2_id'), table_name='couples')
    op.drop_index(op.f('ix_couples_user1_id'), table_name='couples')
    op.drop_table('couples')
