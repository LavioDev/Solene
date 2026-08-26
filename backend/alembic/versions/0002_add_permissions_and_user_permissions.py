"""add_permissions_and_user_permissions

Revision ID: 0002_add_permissions
Revises: 0001_initial_schema
Create Date: 2026-08-26 16:10:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_permissions'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. permissions table
    permissions_table = op.create_table(
        'permissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
    op.create_index(op.f('ix_permissions_module'), 'permissions', ['module'], unique=False)

    # 2. user_permissions table
    op.create_table(
        'user_permissions',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('permission_id', sa.UUID(), nullable=False),
        sa.Column('assigned_by', sa.UUID(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('user_id', 'permission_id')
    )

    # 3. Seed standard default permissions
    seed_permissions = [
        {
            "id": uuid.uuid4(),
            "code": "users:read",
            "name": "Xem danh sách & chi tiết người dùng",
            "module": "users",
            "description": "Cho phép xem danh sách và thông tin chi tiết người dùng (role user)",
        },
        {
            "id": uuid.uuid4(),
            "code": "users:create",
            "name": "Tạo tài khoản người dùng",
            "module": "users",
            "description": "Cho phép tạo mới tài khoản người dùng với role user",
        },
        {
            "id": uuid.uuid4(),
            "code": "users:update",
            "name": "Cập nhật thông tin người dùng",
            "module": "users",
            "description": "Cho phép chỉnh sửa thông tin người dùng (role user)",
        },
        {
            "id": uuid.uuid4(),
            "code": "users:toggle_status",
            "name": "Khóa / Mở khóa người dùng",
            "module": "users",
            "description": "Cho phép kích hoạt hoặc vô hiệu hóa tài khoản người dùng",
        },
        {
            "id": uuid.uuid4(),
            "code": "couples:read",
            "name": "Xem danh sách & chi tiết cặp đôi",
            "module": "couples",
            "description": "Cho phép xem danh sách và hồ sơ cặp đôi",
        },
        {
            "id": uuid.uuid4(),
            "code": "couples:create",
            "name": "Tạo hồ sơ cặp đôi",
            "module": "couples",
            "description": "Cho phép tạo mới liên kết cặp đôi",
        },
        {
            "id": uuid.uuid4(),
            "code": "couples:update",
            "name": "Cập nhật hồ sơ cặp đôi",
            "module": "couples",
            "description": "Cho phép cập nhật thông tin cặp đôi",
        },
    ]
    op.bulk_insert(permissions_table, seed_permissions)


def downgrade() -> None:
    op.drop_table('user_permissions')
    op.drop_index(op.f('ix_permissions_module'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')
