from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_failure_reason"
down_revision = "0001_week6_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cv_uploads", sa.Column("failure_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("cv_uploads", "failure_reason")
