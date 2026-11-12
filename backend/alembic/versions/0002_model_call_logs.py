"""添加模型名称字段与模型调用计量表。

覆盖阶段 3（model_configs.model、model_call_logs 表）与「用量与成本统计」（task_type/task_id）的数据库变更。

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-12
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "model_configs",
        sa.Column("model", sa.String(100), nullable=False, server_default="gpt-4o"),
    )

    op.create_table(
        "model_call_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.BigInteger(), nullable=True),
        sa.Column("model_config_id", sa.BigInteger(), nullable=True),
        sa.Column("agent", sa.String(50), nullable=False),
        sa.Column("task_type", sa.String(20), nullable=True),
        sa.Column("task_id", sa.BigInteger(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_model_call_logs_project", "model_call_logs", ["project_id"])
    op.create_index("idx_model_call_logs_model", "model_call_logs", ["model_config_id"])
    op.create_index("idx_model_call_logs_task", "model_call_logs", ["task_type", "task_id"])


def downgrade() -> None:
    op.drop_index("idx_model_call_logs_task", table_name="model_call_logs")
    op.drop_index("idx_model_call_logs_model", table_name="model_call_logs")
    op.drop_index("idx_model_call_logs_project", table_name="model_call_logs")
    op.drop_table("model_call_logs")
    op.drop_column("model_configs", "model")
