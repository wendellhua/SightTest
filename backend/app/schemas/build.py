"""方案建设的请求/响应模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BuildStartRequest(BaseModel):
    version_id: int | None = None


class BuildOut(BaseModel):
    build_id: int
    project_id: int
    status: str
    stage: str | None = None
    progress: int = 0
    message: str | None = None
    plan_incomplete: bool


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    version_no: int
    status: str
    plan_incomplete: bool
    explore_stats: dict[str, Any] | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime


class VersionDetailOut(VersionOut):
    explore_data: dict[str, Any] | None = None
