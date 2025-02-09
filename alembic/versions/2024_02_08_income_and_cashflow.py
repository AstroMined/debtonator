"""Income and cashflow models

Revision ID: 2024_02_08_income_and_cashflow
Revises: 1d26ae49f3b8
Create Date: 2024-02-08 18:56:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2024_02_08_income_and_cashflow'
down_revision = '1d26ae49f3b8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create income table
    op.create_table(
        'income',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deposited', sa.Boolean(), nullable=False, default=False),
        sa.Column('undeposited_amount', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('updated_at', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_income_date', 'income', ['date'])
    op.create_index('idx_income_deposited', 'income', ['deposited'])

    # Create cashflow_forecasts table
    op.create_table(
        'cashflow_forecasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('total_bills', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_income', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('forecast', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_14_day', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_30_day', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_60_day', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_90_day', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('daily_deficit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('yearly_deficit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('required_income', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('hourly_rate_40', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('hourly_rate_30', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('hourly_rate_20', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('updated_at', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cashflow_forecast_date', 'cashflow_forecasts', ['forecast_date'])

def downgrade() -> None:
    op.drop_table('cashflow_forecasts')
    op.drop_table('income')
