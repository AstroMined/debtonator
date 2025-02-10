"""migrate_bills_to_liabilities_and_payments

# pylint: disable=no-member

Revision ID: 5f5c553b9a57
Revises: 
Create Date: 2025-02-10 16:08:15.754074

"""
from typing import Sequence, Union, cast
from datetime import datetime
from decimal import Decimal

from alembic import op
from alembic.operations import Operations
import sqlalchemy as sa
from sqlalchemy import String, Date, Boolean, Numeric, Text, JSON, DateTime, ForeignKey, Table, Column, Integer, MetaData, Connection

# revision identifiers, used by Alembic.
revision: str = '5f5c553b9a57'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    operations = cast(Operations, op)
    # Create new tables
    operations.create_table(
        'liabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recurring', sa.Boolean(), default=False),
        sa.Column('recurrence_pattern', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

    operations.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bill_id', sa.Integer(), sa.ForeignKey('liabilities.id', ondelete='CASCADE'), nullable=True),
        sa.Column('income_id', sa.Integer(), sa.ForeignKey('income.id'), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

    operations.create_table(
        'payment_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), sa.ForeignKey('payments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    operations.create_index('ix_liabilities_due_date', 'liabilities', ['due_date'])
    operations.create_index('ix_payments_payment_date', 'payments', ['payment_date'])
    operations.create_index('ix_payments_bill_id', 'payments', ['bill_id'])
    operations.create_index('ix_payment_sources_payment_id', 'payment_sources', ['payment_id'])
    operations.create_index('ix_payment_sources_account_id', 'payment_sources', ['account_id'])

    # Migrate data if old bills table exists
    connection = cast(Connection, operations.get_bind())
    metadata = MetaData()
    
    try:
        # Try to reflect the bills table
        bills = Table('bills', metadata, autoload_with=connection)
        
        # If bills table exists, migrate the data
        bills_data = connection.execute(sa.select(bills)).fetchall()
        
        for bill in bills_data:
            # Insert into liabilities
            liability_result = connection.execute(
                sa.text("""
                    INSERT INTO liabilities (name, amount, due_date, description, category, recurring, created_at, updated_at)
                    VALUES (:name, :amount, :due_date, :description, :category, :recurring, :created_at, :updated_at)
                    RETURNING id
                """),
                {
                    "name": bill.name,
                    "amount": bill.amount,
                    "due_date": bill.due_date,
                    "description": bill.description if hasattr(bill, 'description') else None,
                    "category": bill.category if hasattr(bill, 'category') else 'Uncategorized',
                    "recurring": bill.recurring if hasattr(bill, 'recurring') else False,
                    "created_at": bill.created_at if hasattr(bill, 'created_at') else datetime.utcnow(),
                    "updated_at": bill.updated_at if hasattr(bill, 'updated_at') else datetime.utcnow()
                }
            )
            liability_id = liability_result.scalar()

            # If bill has payment information, create payment and sources
            if hasattr(bill, 'paid') and bill.paid:
                payment_result = connection.execute(
                    sa.text("""
                        INSERT INTO payments (bill_id, amount, payment_date, category, created_at, updated_at)
                        VALUES (:bill_id, :amount, :payment_date, :category, :created_at, :updated_at)
                        RETURNING id
                    """),
                    {
                        "bill_id": liability_id,
                        "amount": bill.amount,
                        "payment_date": bill.payment_date if hasattr(bill, 'payment_date') else bill.due_date,
                        "category": bill.category if hasattr(bill, 'category') else 'Uncategorized',
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                payment_id = payment_result.scalar()

                # Create payment source using primary account if available
                if hasattr(bill, 'account_id'):
                    connection.execute(
                        sa.text("""
                            INSERT INTO payment_sources (payment_id, account_id, amount, created_at, updated_at)
                            VALUES (:payment_id, :account_id, :amount, :created_at, :updated_at)
                        """),
                        {
                            "payment_id": payment_id,
                            "account_id": bill.account_id,
                            "amount": bill.amount,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    )

        # Drop the old bills table
        operations.drop_table('bills')
    except sa.exc.NoSuchTableError:
        # If bills table doesn't exist, skip migration
        pass


def downgrade() -> None:
    # Drop new tables
    operations = cast(Operations, op)
    operations.drop_table('payment_sources')
    operations.drop_table('payments')
    operations.drop_table('liabilities')
