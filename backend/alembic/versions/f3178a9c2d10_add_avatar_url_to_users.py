"""add_avatar_url_to_users

Revision ID: f3178a9c2d10
Revises: e57208d1c92a
Create Date: 2026-08-22 20:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3178a9c2d10'
down_revision: Union[str, None] = 'e57208d1c92a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
