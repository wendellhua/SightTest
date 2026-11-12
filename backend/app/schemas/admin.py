"""admin 后台的请求/响应模型。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdminUserUpdate(BaseModel):
    status: Literal["normal", "frozen"] | None = None
    reset_password: str | None = Field(default=None, min_length=6, max_length=128)


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    is_admin: bool
    status: str
    created_at: datetime


class AdminProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    creator_id: int
    model_config_id: int | None
    plan_status: str
    created_at: datetime


class PlatformSettingUpdate(BaseModel):
    total_concurrency: int | None = Field(default=None, ge=1)
    global_stress_limit: int | None = Field(default=None, ge=1)
    new_user_stress_limit: int | None = Field(default=None, ge=1)
    default_explore_minutes: int | None = Field(default=None, ge=1)
    default_explore_pages: int | None = Field(default=None, ge=1)
    retention_days: int | None = Field(default=None, ge=1)
    stress_duration_seconds: int | None = Field(default=None, ge=1)
    account_limit: int | None = Field(default=None, ge=1)
    default_account_stress_limit: int | None = Field(default=None, ge=1)
    disclaimer: str | None = None


class PlatformSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_concurrency: int
    global_stress_limit: int
    new_user_stress_limit: int
    default_explore_minutes: int
    default_explore_pages: int
    retention_days: int
    stress_duration_seconds: int
    account_limit: int
    default_account_stress_limit: int
    disclaimer: str | None
    updated_at: datetime
