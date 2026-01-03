"""add vitals to eventtype enum

Revision ID: add_vitals_enum
Revises: 8a528456fbf4
Create Date: 2025-12-31 11:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_vitals_enum'
down_revision: Union[str, None] = '8a528456fbf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'Vitals' value to the eventtype enum
    # Note: ALTER TYPE ... ADD VALUE cannot be run inside a transaction block in PostgreSQL
    # We check if the value exists first to avoid errors on re-runs
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'Vitals' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'eventtype')
            ) THEN
                ALTER TYPE eventtype ADD VALUE 'Vitals';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly
    # This would require recreating the enum type and updating all dependent columns
    # For now, we'll leave a comment indicating manual intervention would be needed
    # In practice, you might need to:
    # 1. Create a new enum without 'Vitals'
    # 2. Update all columns using the old enum to use the new one
    # 3. Drop the old enum
    # 4. Rename the new enum to the original name
    pass

