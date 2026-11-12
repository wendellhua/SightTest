"""测试执行与问题的请求/响应模型。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ExecutionCreate(BaseModel):
    scope: Literal["full", "func", "api", "perf", "mech"]
    case_ids: list[int] | None = None


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    plan_version_id: int | None
    plan_version_no: int
    name: str
    scope: str
    is_debug: bool
    status: str
    progress: int
    order_items: list[Any] | None
    summary: dict[str, Any] | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class CaseExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    execution_id: int
    plan_version_id: int | None
    result: str
    evidence: dict[str, Any] | None
    case_snapshot: dict[str, Any] | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    execution_id: int
    page: str
    severity: str
    description: str
    status: str
    screenshot_ref: str | None
    created_at: datetime


class IssueUpdate(BaseModel):
    status: Literal["open", "misreported"]


class MisreportPatternOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    page: str
    description: str
    status: str
    created_at: datetime


class MisreportPatternUpdate(BaseModel):
    status: Literal["revoked"]
