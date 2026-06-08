"""add_conflicts_table

Revision ID: 2b7e9b03a045
Revises: 5e8473ac9901
Create Date: 2026-06-08 13:12:37.026392
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2b7e9b03a045'
down_revision: Union[str, None] = '5e8473ac9901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conflicts',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('task_id', sa.UUID(), sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('agent_id', sa.UUID(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('other_agent_id', sa.UUID(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('old_hash', sa.String(length=64), nullable=False),
        sa.Column('current_hash', sa.String(length=64), nullable=False),
        sa.Column('current_content', sa.Text(), nullable=False),
        sa.Column('new_content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('action', sa.String(length=30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('conflicts')
