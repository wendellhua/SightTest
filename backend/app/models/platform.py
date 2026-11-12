"""平台设置模型：platform_settings（单行）。"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, SmallInteger, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlatformSetting(Base):
    """平台级设置，单行记录（id 恒为 1）。"""

    __tablename__ = "platform_settings"
    __table_args__ = (CheckConstraint("id = 1", name="ck_platform_settings_singleton"),)

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    total_concurrency: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    global_stress_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    new_user_stress_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("50"))
    default_explore_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("60"))
    default_explore_pages: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("200"))
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("90"))
    stress_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("60"))
    account_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    default_account_stress_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
