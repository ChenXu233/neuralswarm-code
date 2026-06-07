"""add project_type and client_id to projects

Revision ID: c395703d6be7
Revises: 9ba95ab9b4f9
Create Date: 2026-06-07 22:16:46.464568
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c395703d6be7'
down_revision: Union[str, None] = '9ba95ab9b4f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('project_type', sa.String(length=20), server_default='cloud', nullable=False))
    op.add_column('projects', sa.Column('client_id', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('projects', 'client_id')
    op.drop_column('projects', 'project_type')
