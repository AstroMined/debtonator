"""change_payment_date_to_datetime

Revision ID: 12a0ff8f2088
Revises: b7b53c9c2a40
Create Date: 2025-02-15 12:35:57.449158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12a0ff8f2088'
down_revision: Union[str, None] = 'b7b53c9c2a40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary column with DateTime
    op.add_column('payments', sa.Column('payment_datetime', sa.DateTime(), nullable=True))
    
    # Copy data from date to datetime, setting time to midnight UTC
    op.execute("""
        UPDATE payments 
        SET payment_datetime = payment_date::timestamp + '00:00:00'::time at time zone 'UTC'
    """)
    
    # Drop the old column
    op.drop_column('payments', 'payment_date')
    
    # Rename the new column to payment_date
    op.alter_column('payments', 'payment_datetime', new_column_name='payment_date')
    
    # Make it not nullable
    op.alter_column('payments', 'payment_date', nullable=False)


def downgrade() -> None:
    # Create a temporary column with Date
    op.add_column('payments', sa.Column('payment_date_old', sa.Date(), nullable=True))
    
    # Copy data from datetime to date
    op.execute("""
        UPDATE payments 
        SET payment_date_old = payment_date::date
    """)
    
    # Drop the datetime column
    op.drop_column('payments', 'payment_date')
    
    # Rename the date column to payment_date
    op.alter_column('payments', 'payment_date_old', new_column_name='payment_date')
    
    # Make it not nullable
    op.alter_column('payments', 'payment_date', nullable=False)
