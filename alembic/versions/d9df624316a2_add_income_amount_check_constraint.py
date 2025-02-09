"""add_income_amount_check_constraint

Revision ID: d9df624316a2
Revises: d1d05c03f5e8
Create Date: 2025-02-09 13:39:20.885006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import CheckConstraint
from alembic.operations import ops


# revision identifiers, used by Alembic.
revision: str = 'd9df624316a2'
down_revision: Union[str, None] = 'd1d05c03f5e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('income') as batch_op:
        batch_op.create_check_constraint(
            'ck_income_positive_amount',
            'amount >= 0'
        )


def downgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('income') as batch_op:
        batch_op.drop_constraint('ck_income_positive_amount')
