"""模型调用计量模型：model_call_logs。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModelCallLog(Base):
    """模型调用计量（token 用量）。"""

    __tablename__ = "model_call_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    model_config_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    agent: Mapped[str] = mapped_column(String(50), nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    task_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
