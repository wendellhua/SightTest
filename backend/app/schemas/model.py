"""模型配置的请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    base_url: str = Field(min_length=1, max_length=500)
    api_key: str = Field(min_length=1, max_length=500)
    model: str = Field(min_length=1, max_length=100)


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    base_url: str | None = Field(default=None, min_length=1, max_length=500)
    api_key: str | None = Field(default=None, min_length=1, max_length=500)
    model: str | None = Field(default=None, min_length=1, max_length=100)


class ModelCheckResponse(BaseModel):
    ok: bool
    supports_vision: bool
    message: str


class ModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    base_url: str
    model: str
    status: str
    created_at: datetime
    updated_at: datetime
