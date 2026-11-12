"""基线迁移。

初始表结构由权威脚本 `scripts/sql/schema.sql` 创建，本迁移仅建立 Alembic 基线，
后续所有表结构变更通过 `alembic revision --autogenerate` 生成迁移。

Revision ID: 0001
Revises:
Create Date: 2026-11-11
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
