"""create_activity_logs_table

Revision ID: a1b2c3d4e5f6
Revises: 28eb5bc32122
Create Date: 2026-06-03 00:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '28eb5bc32122'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('subject_type', sa.String(length=255), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('causer_type', sa.String(length=255), nullable=True),
        sa.Column('causer_id', sa.Integer(), nullable=True),
        sa.Column('event', sa.String(length=50), nullable=False),
        sa.Column('old_properties', sa.JSON(), nullable=True),
        sa.Column('new_properties', sa.JSON(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_activity_logs_event'), 'activity_logs', ['event'], unique=False
    )
    op.create_index(
        op.f('ix_activity_logs_causer_id'),
        'activity_logs',
        ['causer_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_activity_logs_causer_id'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_event'), table_name='activity_logs')
    op.drop_table('activity_logs')
