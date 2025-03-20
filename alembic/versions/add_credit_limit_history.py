"""add credit limit history

Revision ID: add_credit_limit_history
Revises:
Create Date: 2025-02-12 16:59:31.000000

"""

from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_credit_limit_history"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create credit_limit_history table
    op.create_table(
        "credit_limit_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("credit_limit", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index for efficient lookups
    op.create_index(
        "idx_credit_limit_history_account_date",
        "credit_limit_history",
        ["account_id", "effective_date"],
    )


def downgrade() -> None:
    # Drop the credit_limit_history table
    op.drop_table("credit_limit_history")
