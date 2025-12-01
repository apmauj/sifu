"""Initial baseline for UI, UR, Exchange, and BROU tables

Revision ID: 001_initial_baseline
Revises: 
Create Date: 2025-10-15 21:53:52.034803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ui_records table
    op.create_table(
        'ui_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', name='uq_ui_date'),
    )
    op.create_index(op.f('ix_ui_records_date'), 'ui_records', ['date'], unique=True)
    op.create_index(op.f('ix_ui_records_id'), 'ui_records', ['id'], unique=False)

    # Create ur_records table
    op.create_table(
        'ur_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year', 'month', name='uq_ur_year_month'),
    )
    op.create_index(op.f('ix_ur_records_id'), 'ur_records', ['id'], unique=False)
    op.create_index(op.f('ix_ur_records_year'), 'ur_records', ['year'], unique=False)
    op.create_index(op.f('ix_ur_records_month'), 'ur_records', ['month'], unique=False)

    # Create exchange_rate_records table
    op.create_table(
        'exchange_rate_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('buy_rate', sa.Float(), nullable=True),
        sa.Column('sell_rate', sa.Float(), nullable=True),
        sa.Column('average_rate', sa.Float(), nullable=True),
        sa.Column('arbitrage', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'currency', name='uq_exchange_rate_date_currency'),
    )
    op.create_index(op.f('ix_exchange_rate_records_date'), 'exchange_rate_records', ['date'], unique=False)
    op.create_index(op.f('ix_exchange_rate_records_currency'), 'exchange_rate_records', ['currency'], unique=False)

    # Create brou_records table
    op.create_table(
        'brou_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(20), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('buy_rate', sa.Float(), nullable=True),
        sa.Column('sell_rate', sa.Float(), nullable=True),
        sa.Column('average_rate', sa.Float(), nullable=True),
        sa.Column('arbitrage_buy', sa.Float(), nullable=True),
        sa.Column('arbitrage_sell', sa.Float(), nullable=True),
        sa.Column('source', sa.String(20), nullable=False, server_default='BROU'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('currency', 'timestamp', name='uq_brou_currency_timestamp'),
    )
    op.create_index(op.f('ix_brou_records_currency'), 'brou_records', ['currency'], unique=False)
    op.create_index(op.f('ix_brou_records_timestamp'), 'brou_records', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_brou_records_timestamp'), table_name='brou_records')
    op.drop_index(op.f('ix_brou_records_currency'), table_name='brou_records')
    op.drop_table('brou_records')

    op.drop_index(op.f('ix_exchange_rate_records_currency'), table_name='exchange_rate_records')
    op.drop_index(op.f('ix_exchange_rate_records_date'), table_name='exchange_rate_records')
    op.drop_table('exchange_rate_records')

    op.drop_index(op.f('ix_ur_records_month'), table_name='ur_records')
    op.drop_index(op.f('ix_ur_records_year'), table_name='ur_records')
    op.drop_index(op.f('ix_ur_records_id'), table_name='ur_records')
    op.drop_table('ur_records')

    op.drop_index(op.f('ix_ui_records_id'), table_name='ui_records')
    op.drop_index(op.f('ix_ui_records_date'), table_name='ui_records')
    op.drop_table('ui_records')
