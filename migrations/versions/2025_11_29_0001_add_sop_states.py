"""add sop_states table

Revision ID: 20251129_0001
Revises: 
Create Date: 2025-11-29
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251129_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sop_states",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False, index=True),
        sa.Column("contact_id", sa.String(length=36), sa.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("current_step", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sop_states")
