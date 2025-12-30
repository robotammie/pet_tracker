"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create app_user table
    op.create_table('app_user',
    sa.Column('uuid', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_app_user_email'), 'app_user', ['email'], unique=False)
    
    # Create household table
    op.create_table('household',
    sa.Column('uuid', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_household_email'), 'household', ['email'], unique=False)
    
    # Create pet table
    op.create_table('pet',
    sa.Column('uuid', sa.String(length=64), nullable=False),
    sa.Column('household_uuid', sa.String(length=64), nullable=True),
    sa.Column('species', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('birthdate', sa.DateTime(timezone=True), nullable=True),
    sa.Column('photo_addr', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['household_uuid'], ['household.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    
    # Create user_household table
    op.create_table('user_household',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=False),
    sa.Column('household_id', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['household_id'], ['household.uuid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create event table
    op.create_table('event',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('household_uuid', sa.String(length=64), nullable=False),
    sa.Column('pet_uuid', sa.String(length=64), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('meta', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['app_user.uuid'], ),
    sa.ForeignKeyConstraint(['household_uuid'], ['household.uuid'], ),
    sa.ForeignKeyConstraint(['pet_uuid'], ['pet.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_type'), 'event', ['type'], unique=False)
    
    # Create food_meta table
    op.create_table('food_meta',
    sa.Column('uuid', sa.String(length=64), nullable=False),
    sa.Column('household_uuid', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('serving_size', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=64), nullable=False),
    sa.Column('calories', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['household_uuid'], ['household.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('food_meta')
    op.drop_index(op.f('ix_event_type'), table_name='event')
    op.drop_table('event')
    op.drop_table('user_household')
    op.drop_table('pet')
    op.drop_index(op.f('ix_household_email'), table_name='household')
    op.drop_table('household')
    op.drop_index(op.f('ix_app_user_email'), table_name='app_user')
    op.drop_table('app_user')

