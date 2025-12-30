"""Add archived column to food_meta

Revision ID: 002_archived
Revises: 001_initial
Create Date: 2025-01-27 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_archived'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add archived column to food_meta table
    # Set default to False for existing rows
    op.add_column('food_meta', 
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    # Remove archived column from food_meta table
    op.drop_column('food_meta', 'archived')

