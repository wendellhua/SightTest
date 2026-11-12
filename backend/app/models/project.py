"""项目相关模型：projects / test_accounts。"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Project(Base):
    """项目（被测网站）。"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    creator_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    model_config_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    plan_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'empty'"))
    plan_incomplete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    active_discovery: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TestAccount(Base):
    """项目测试账号（每个项目至少 1 个）。"""

    __tablename__ = "test_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    last_login_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_login_fail_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
