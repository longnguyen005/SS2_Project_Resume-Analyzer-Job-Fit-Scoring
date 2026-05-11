from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_cloud_storage_metadata"
down_revision = "0002_failure_reason"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cv_uploads", sa.Column("storage_key", sa.String(length=500), nullable=True))
    op.add_column("cv_uploads", sa.Column("storage_url", sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column("cv_uploads", "storage_url")
    op.drop_column("cv_uploads", "storage_key")
