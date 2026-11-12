"""用例的请求/响应模型。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CaseType = Literal["func", "api", "perf", "mech"]
Priority = Literal["P0", "P1", "P2", "P3"]


class CaseCreate(BaseModel):
    case_type: CaseType
    module_path: str | None = Field(default=None, max_length=500)
    page: str | None = Field(default=None, max_length=500)
    name: str = Field(min_length=1, max_length=255)
    priority: Priority = "P2"
    precondition: str | None = None
    steps: str = Field(min_length=1)
    expect: str = Field(min_length=1)
    automatable: bool = True
    remark: str | None = Field(default=None, max_length=255)
    flags: dict[str, Any] | None = None
    extension: dict[str, Any] | None = None


class CaseUpdate(BaseModel):
    case_type: CaseType | None = None
    module_path: str | None = Field(default=None, max_length=500)
    page: str | None = Field(default=None, max_length=500)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    priority: Priority | None = None
    precondition: str | None = None
    steps: str | None = Field(default=None, min_length=1)
    expect: str | None = Field(default=None, min_length=1)
    automatable: bool | None = None
    remark: str | None = Field(default=None, max_length=255)
    flags: dict[str, Any] | None = None
    extension: dict[str, Any] | None = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    plan_version_id: int
    case_type: str
    module_path: str | None
    page: str | None
    name: str
    priority: str
    precondition: str | None
    steps: str
    expect: str
    automatable: bool
    result: str
    remark: str | None
    flags: dict[str, Any] | None
    extension: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
