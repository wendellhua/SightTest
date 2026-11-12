"""方案版本模型：plan_versions。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlanVersion(Base):
    """方案版本（一次方案建设/重新探索产出）。"""

    __tablename__ = "plan_versions"
    __table_args__ = (UniqueConstraint("project_id", "version_no", name="uq_plan_versions_no"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'building'"))
    plan_incomplete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    explore_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    explore_stats: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
