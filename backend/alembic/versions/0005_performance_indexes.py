from __future__ import annotations

from alembic import op


revision = "0005_performance_indexes"
down_revision = "0004_failed_stage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # These indexes may already exist in local/dev databases that were
    # created from earlier model metadata or parallel branches.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_cv_uploads_user_id_created_at "
        "ON cv_uploads (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_analysis_results_cv_upload_id "
        "ON analysis_results (cv_upload_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_job_descriptions_user_id "
        "ON job_descriptions (user_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_job_descriptions_user_id")
    op.execute("DROP INDEX IF EXISTS ix_analysis_results_cv_upload_id")
    op.execute("DROP INDEX IF EXISTS ix_cv_uploads_user_id_created_at")
