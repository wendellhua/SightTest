"""认证与账号相关的请求/响应模型。"""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

# 邮箱统一去空格并转小写，避免大小写不同被视为两个账号
NormalizedEmail = Annotated[EmailStr, AfterValidator(lambda v: v.strip().lower())]


class SendCodeRequest(BaseModel):
    email: NormalizedEmail
    purpose: Literal["register", "reset_password"]


class RegisterRequest(BaseModel):
    email: NormalizedEmail
    code: str = Field(min_length=6, max_length=16)
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: NormalizedEmail
    password: str = Field(min_length=1, max_length=64)


class ResetPasswordRequest(BaseModel):
    email: NormalizedEmail
    code: str = Field(min_length=6, max_length=16)
    new_password: str = Field(min_length=8, max_length=64)


class UpdateProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    is_admin: bool
    status: str
    admin_password_changed: bool
    created_at: datetime


class TokenResponse(BaseModel):
    token: str
    user: UserOut
