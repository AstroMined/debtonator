"""remove_hardcoded_accounts

Revision ID: e9caf0c10db0
Revises: 2024_02_08_income_and_cashflow
Create Date: 2024-02-08 21:38:23.123456

"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = 'e9caf0c10db0'
down_revision: Union[str, None] = '2024_02_08_income_and_cashflow'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create bill_splits table
    op.create_table(
        'bill_splits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bill_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE'), onupdate=sa.text('CURRENT_DATE')),
        sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bill_id', 'account_id', name='uq_bill_account_split')
    )
    op.create_index('idx_bill_splits_bill_id', 'bill_splits', ['bill_id'])
    op.create_index('idx_bill_splits_account_id', 'bill_splits', ['account_id'])

    # Create temporary tables for data migration
    bills = table(
        'bills',
        column('id', sa.Integer),
        column('account_id', sa.Integer),
        column('amex_amount', sa.Numeric),
        column('unlimited_amount', sa.Numeric),
        column('ufcu_amount', sa.Numeric)
    )

    accounts = table(
        'accounts',
        column('id', sa.Integer),
        column('name', sa.String)
    )

    bill_splits = table(
        'bill_splits',
        column('bill_id', sa.Integer),
        column('account_id', sa.Integer),
        column('amount', sa.Numeric)
    )

    # Get connection for data migration
    connection = op.get_bind()

    # Get account IDs by name
    account_map = {}
    for account in connection.execute(accounts.select()):
        account_map[account.name.upper()] = account.id

    # Migrate existing split amounts to new table
    for bill in connection.execute(bills.select()):
        if bill.amex_amount and bill.amex_amount > 0 and 'AMEX' in account_map:
            connection.execute(
                bill_splits.insert().values(
                    bill_id=bill.id,
                    account_id=account_map['AMEX'],
                    amount=bill.amex_amount
                )
            )
        
        if bill.unlimited_amount and bill.unlimited_amount > 0 and 'UNLIMITED' in account_map:
            connection.execute(
                bill_splits.insert().values(
                    bill_id=bill.id,
                    account_id=account_map['UNLIMITED'],
                    amount=bill.unlimited_amount
                )
            )
        
        if bill.ufcu_amount and bill.ufcu_amount > 0 and 'UFCU' in account_map:
            connection.execute(
                bill_splits.insert().values(
                    bill_id=bill.id,
                    account_id=account_map['UFCU'],
                    amount=bill.ufcu_amount
                )
            )

    # Remove old columns
    op.drop_column('bills', 'amex_amount')
    op.drop_column('bills', 'unlimited_amount')
    op.drop_column('bills', 'ufcu_amount')


def downgrade() -> None:
    # Add back the old columns
    op.add_column('bills', sa.Column('amex_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('bills', sa.Column('unlimited_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('bills', sa.Column('ufcu_amount', sa.Numeric(10, 2), nullable=True))

    # Create temporary tables for data migration
    bills = table(
        'bills',
        column('id', sa.Integer),
        column('amex_amount', sa.Numeric),
        column('unlimited_amount', sa.Numeric),
        column('ufcu_amount', sa.Numeric)
    )

    accounts = table(
        'accounts',
        column('id', sa.Integer),
        column('name', sa.String)
    )

    bill_splits = table(
        'bill_splits',
        column('bill_id', sa.Integer),
        column('account_id', sa.Integer),
        column('amount', sa.Numeric)
    )

    # Get connection for data migration
    connection = op.get_bind()

    # Get account IDs by name
    account_map = {}
    for account in connection.execute(accounts.select()):
        name = account.name.upper()
        if name in ['AMEX', 'UNLIMITED', 'UFCU']:
            account_map[account.id] = name

    # Migrate data back to old columns
    for split in connection.execute(bill_splits.select()):
        if split.account_id in account_map:
            account_name = account_map[split.account_id]
            column_name = f"{account_name.lower()}_amount"
            
            connection.execute(
                bills.update()
                .where(bills.c.id == split.bill_id)
                .values(**{column_name: split.amount})
            )

    # Drop the bill_splits table
    op.drop_table('bill_splits')
