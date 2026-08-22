"""add_tasks_table

Revision ID: e57208d1c92a
Revises: 480118763c46
Create Date: 2026-08-22 13:14:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e57208d1c92a'
down_revision: Union[str, None] = '480118763c46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', sa.String(length=50), server_default='medium', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_is_completed'), 'tasks', ['is_completed'], unique=False)
    op.create_index(op.f('ix_tasks_start_time'), 'tasks', ['start_time'], unique=False)
    op.create_index(op.f('ix_tasks_end_time'), 'tasks', ['end_time'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_end_time'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_start_time'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_is_completed'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_table('tasks')
