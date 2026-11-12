"""报告的请求/响应模型。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    scope: Literal["execution", "snapshot"]
    execution_id: int | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    scope: str
    execution_id: int | None
    status: str
    score: int
    risk_level: str
    top_issues: list[Any] | None
    summary: str | None
    content_ref: str | None
    created_at: datetime
