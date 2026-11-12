"""模型配置模型：model_configs。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModelConfig(Base):
    """模型配置收集表（归属用户）。"""

    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'gpt-4o'"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'unverified'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
