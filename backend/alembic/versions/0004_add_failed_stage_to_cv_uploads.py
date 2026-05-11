from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_failed_stage"
down_revision = "0003_cloud_storage_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cv_uploads", sa.Column("failed_stage", sa.String(length=30), nullable=True))


def downgrade() -> None:
    op.drop_column("cv_uploads", "failed_stage")
