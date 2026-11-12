"""验证码失败次数字段与平台设置初始行。

- email_verifications.failed_attempts：限制验证码错误尝试次数，防止暴力破解
- platform_settings：写入单行默认记录（id=1），后台「平台设置」依赖该行

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-12
"""

import sqlalchemy as sa

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "email_verifications",
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute("INSERT INTO platform_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING")


def downgrade() -> None:
    op.drop_column("email_verifications", "failed_attempts")
