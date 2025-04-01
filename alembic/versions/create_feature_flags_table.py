"""Create feature flags table

Revision ID: 2025040101
Revises: add_credit_limit_history
Create Date: 2025-04-01 16:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '2025040101'
down_revision = 'add_credit_limit_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use JSON if the database supports it, otherwise use String
    try:
        json_type = JSON()
    except:
        json_type = sa.String()
        
    op.create_table(
        'feature_flags',
        sa.Column('name', sa.String(255), primary_key=True, nullable=False, index=True),
        sa.Column('flag_type', sa.String(50), nullable=False),
        sa.Column('value', json_type, nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('metadata', json_type, nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_feature_flags_flag_type', 'feature_flags', ['flag_type'])
    op.create_index('ix_feature_flags_is_system', 'feature_flags', ['is_system'])


def downgrade() -> None:
    op.drop_index('ix_feature_flags_is_system')
    op.drop_index('ix_feature_flags_flag_type')
    op.drop_table('feature_flags')
