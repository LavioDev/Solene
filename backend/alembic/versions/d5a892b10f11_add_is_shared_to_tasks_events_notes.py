"""add_is_shared_to_tasks_events_notes

Revision ID: d5a892b10f11
Revises: b4129c51a702
Create Date: 2026-08-23 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5a892b10f11'
down_revision: Union[str, None] = 'b4129c51a702'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_shared to tasks
    op.add_column(
        'tasks',
        sa.Column('is_shared', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )
    op.create_index(op.f('ix_tasks_is_shared'), 'tasks', ['is_shared'], unique=False)

    # 2. Add is_shared to special_events
    op.add_column(
        'special_events',
        sa.Column('is_shared', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )
    op.create_index(op.f('ix_special_events_is_shared'), 'special_events', ['is_shared'], unique=False)

    # 3. Add is_shared to user_notes
    op.add_column(
        'user_notes',
        sa.Column('is_shared', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )
    op.create_index(op.f('ix_user_notes_is_shared'), 'user_notes', ['is_shared'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_notes_is_shared'), table_name='user_notes')
    op.drop_column('user_notes', 'is_shared')

    op.drop_index(op.f('ix_special_events_is_shared'), table_name='special_events')
    op.drop_column('special_events', 'is_shared')

    op.drop_index(op.f('ix_tasks_is_shared'), table_name='tasks')
    op.drop_column('tasks', 'is_shared')
