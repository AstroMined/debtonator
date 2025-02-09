"""add_account_id_to_income

Revision ID: d1d05c03f5e8
Revises: e9caf0c10db0
Create Date: 2025-02-09 12:58:29.911491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic.operations import ops


# revision identifiers, used by Alembic.
revision: str = 'd1d05c03f5e8'
down_revision: Union[str, None] = 'e9caf0c10db0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a new table with all columns including the new one
    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_income_account_id',
            'accounts',
            ['account_id'], ['id']
        )
        batch_op.create_index(
            'idx_income_account_id',
            ['account_id']
        )

def downgrade() -> None:
    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.drop_index('idx_income_account_id')
        batch_op.drop_constraint('fk_income_account_id', type_='foreignkey')
        batch_op.drop_column('account_id')
