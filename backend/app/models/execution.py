"""测试执行相关模型：executions / case_executions / issues / issue_cases / misreport_patterns。"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Execution(Base):
    """测试执行任务（含调试执行，is_debug 标记）。"""

    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    plan_version_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    plan_version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    is_debug: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'queued'"))
    progress: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    order_items: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CaseExecution(Base):
    """用例级执行记录（历史结果 + 证据，含用例快照）。"""

    __tablename__ = "case_executions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    execution_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    plan_version_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    case_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Issue(Base):
    """主动发现的问题。"""

    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    execution_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    page: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'open'"))
    screenshot_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class IssueCase(Base):
    """问题与用例的多对多关联。"""

    __tablename__ = "issue_cases"
    __table_args__ = (UniqueConstraint("issue_id", "case_id", name="uq_issue_cases"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    issue_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    case_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)


class MisreportPattern(Base):
    """误报忽略清单（可撤销）。"""

    __tablename__ = "misreport_patterns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    page: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
