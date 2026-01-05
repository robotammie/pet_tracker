"""empty message

Revision ID: 1620aefe6fee
Revises: c6c00ddb26c9
Create Date: 2026-01-04 12:14:14.559888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1620aefe6fee'
down_revision: Union[str, None] = 'c6c00ddb26c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('saved_event', sa.Column('name', sa.String(length=64), nullable=True))
    op.alter_column('saved_event', 'meta',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)


def downgrade() -> None:
    op.alter_column('saved_event', 'meta',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.drop_column('saved_event', 'name')

