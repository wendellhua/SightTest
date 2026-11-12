"""用户设置的请求/响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


class SettingUpdate(BaseModel):
    explore_minutes: int | None = Field(default=None, ge=1, le=600)
    explore_pages: int | None = Field(default=None, ge=1, le=10000)
    stress_limit: int | None = Field(default=None, ge=1, le=1000)
    account_stress_limit: int | None = Field(default=None, ge=1, le=100)


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    explore_minutes: int
    explore_pages: int
    stress_limit: int
    account_stress_limit: int
