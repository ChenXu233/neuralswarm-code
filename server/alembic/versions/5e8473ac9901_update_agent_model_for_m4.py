"""update_agent_model_for_m4

Revision ID: 5e8473ac9901
Revises: c395703d6be7
Create Date: 2026-06-08 11:48:44.500041
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5e8473ac9901'
down_revision: Union[str, None] = 'c395703d6be7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to agents table
    op.add_column('agents', sa.Column('agent_type', sa.String(length=20), server_default='worker', nullable=False))
    op.add_column('agents', sa.Column('task_id', sa.UUID(), nullable=True))
    op.add_column('agents', sa.Column('parent_id', sa.UUID(), nullable=True))
    op.add_column('agents', sa.Column('llm_config', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('agents', sa.Column('worktree_path', sa.Text(), nullable=True))

    # Add foreign key constraints
    op.create_foreign_key('agents_task_id_fkey', 'agents', 'tasks', ['task_id'], ['id'])
    op.create_foreign_key('agents_parent_id_fkey', 'agents', 'agents', ['parent_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraints
    op.drop_constraint('agents_parent_id_fkey', 'agents', type_='foreignkey')
    op.drop_constraint('agents_task_id_fkey', 'agents', type_='foreignkey')

    # Remove new columns
    op.drop_column('agents', 'worktree_path')
    op.drop_column('agents', 'llm_config')
    op.drop_column('agents', 'parent_id')
    op.drop_column('agents', 'task_id')
    op.drop_column('agents', 'agent_type')
