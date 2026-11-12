"""用例模型：cases。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Case(Base):
    """测试用例（功能/接口/页面加载/接口压测/网站机制）。"""

    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    plan_version_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    case_type: Mapped[str] = mapped_column(String(20), nullable=False)
    module_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page: Mapped[str | None] = mapped_column(String(500), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'P2'"))
    precondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[str] = mapped_column(Text, nullable=False)
    expect: Mapped[str] = mapped_column(Text, nullable=False)
    automatable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    result: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'none'"))
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    flags: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extension: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
