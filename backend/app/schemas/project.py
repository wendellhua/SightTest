"""项目与测试账号的请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountIn(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)
    is_primary: bool = False


class AccountUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=1, max_length=255)
    is_primary: bool | None = None


class UrlCheckRequest(BaseModel):
    url: str = Field(min_length=1, max_length=500)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=500)
    model_config_id: int | None = None
    accounts: list[AccountIn] = Field(min_length=1)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    model_config_id: int | None = None
    active_discovery: bool | None = None


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    username: str
    is_primary: bool
    last_login_status: str | None
    last_login_fail_reason: str | None
    last_login_at: datetime | None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    creator_id: int
    model_config_id: int | None
    plan_status: str
    plan_incomplete: bool
    active_discovery: bool
    created_at: datetime
    updated_at: datetime
