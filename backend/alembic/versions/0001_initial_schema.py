"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-23 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. couples
    op.create_table(
        'couples',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user1_id', sa.Uuid(), nullable=False),
        sa.Column('user2_id', sa.Uuid(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('nickname', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('cover_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_couples_user1_id'), 'couples', ['user1_id'], unique=False)
    op.create_index(op.f('ix_couples_user2_id'), 'couples', ['user2_id'], unique=False)

    # 3. devices
    op.create_table(
        'devices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('device_code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('mac_address', sa.String(length=32), nullable=True),
        sa.Column('chip_type', sa.String(length=64), nullable=False),
        sa.Column('hardware_capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('current_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_device_code'), 'devices', ['device_code'], unique=True)
    op.create_index(op.f('ix_devices_mac_address'), 'devices', ['mac_address'], unique=True)

    # 4. telemetry_logs
    op.create_table(
        'telemetry_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.UUID(), nullable=False),
        sa.Column('cpu_temperature', sa.Float(), nullable=True),
        sa.Column('free_heap', sa.Integer(), nullable=True),
        sa.Column('wifi_rssi', sa.Integer(), nullable=True),
        sa.Column('battery_voltage', sa.Float(), nullable=True),
        sa.Column('custom_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetry_logs_device_id'), 'telemetry_logs', ['device_id'], unique=False)

    # 5. special_events
    op.create_table(
        'special_events',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('anchor_date', sa.Date(), nullable=False),
        sa.Column('recurrence_type', sa.String(length=50), nullable=False),
        sa.Column('interval_value', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_special_events_is_shared'), 'special_events', ['is_shared'], unique=False)
    op.create_index(op.f('ix_special_events_user_id'), 'special_events', ['user_id'], unique=False)

    # 6. user_moods
    op.create_table(
        'user_moods',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('mood_score', sa.Integer(), nullable=False),
        sa.Column('mood_tag', sa.String(length=50), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('activities', sa.String(length=255), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'entry_date', name='uq_user_mood_entry_date')
    )
    op.create_index(op.f('ix_user_moods_entry_date'), 'user_moods', ['entry_date'], unique=False)
    op.create_index(op.f('ix_user_moods_is_shared'), 'user_moods', ['is_shared'], unique=False)
    op.create_index(op.f('ix_user_moods_user_id'), 'user_moods', ['user_id'], unique=False)

    # 7. tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('is_shared', sa.Boolean(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_end_time'), 'tasks', ['end_time'], unique=False)
    op.create_index(op.f('ix_tasks_is_completed'), 'tasks', ['is_completed'], unique=False)
    op.create_index(op.f('ix_tasks_is_shared'), 'tasks', ['is_shared'], unique=False)
    op.create_index(op.f('ix_tasks_start_time'), 'tasks', ['start_time'], unique=False)
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)

    # 8. memories
    op.create_table(
        'memories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('display_type', sa.String(length=50), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memories_is_shared'), 'memories', ['is_shared'], unique=False)
    op.create_index(op.f('ix_memories_user_id'), 'memories', ['user_id'], unique=False)

    # 9. memory_images
    op.create_table(
        'memory_images',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('memory_id', sa.Uuid(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memory_images_memory_id'), 'memory_images', ['memory_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_memory_images_memory_id'), table_name='memory_images')
    op.drop_table('memory_images')
    op.drop_index(op.f('ix_memories_user_id'), table_name='memories')
    op.drop_index(op.f('ix_memories_is_shared'), table_name='memories')
    op.drop_table('memories')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_start_time'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_is_shared'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_is_completed'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_end_time'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_user_moods_user_id'), table_name='user_moods')
    op.drop_index(op.f('ix_user_moods_is_shared'), table_name='user_moods')
    op.drop_index(op.f('ix_user_moods_entry_date'), table_name='user_moods')
    op.drop_table('user_moods')
    op.drop_index(op.f('ix_special_events_user_id'), table_name='special_events')
    op.drop_index(op.f('ix_special_events_is_shared'), table_name='special_events')
    op.drop_table('special_events')
    op.drop_index(op.f('ix_telemetry_logs_device_id'), table_name='telemetry_logs')
    op.drop_table('telemetry_logs')
    op.drop_index(op.f('ix_devices_mac_address'), table_name='devices')
    op.drop_index(op.f('ix_devices_device_code'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_couples_user2_id'), table_name='couples')
    op.drop_index(op.f('ix_couples_user1_id'), table_name='couples')
    op.drop_table('couples')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
