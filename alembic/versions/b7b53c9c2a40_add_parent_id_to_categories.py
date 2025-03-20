"""add_parent_id_to_categories

Revision ID: b7b53c9c2a40
Revises: add_credit_limit_history
Create Date: 2025-02-12 21:43:29.889005

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7b53c9c2a40"
down_revision: Union[str, None] = "add_credit_limit_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
