"""账号认证路由：验证码、注册、登录、找回密码。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.response import ok
from app.schemas.auth import LoginRequest, RegisterRequest, ResetPasswordRequest, SendCodeRequest
from app.services import account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-code")
async def send_code(data: SendCodeRequest, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    code = await account.send_code(db, data.email, data.purpose)
    if settings.debug and not settings.smtp_host:
        # 开发环境（SMTP 未配置）验证码无法送达邮箱，直接返回便于联调
        return ok({"dev_code": code})
    return ok()


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return ok(await account.register(db, data))


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return ok(await account.login(db, data.email, data.password))


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    await account.reset_password(db, data)
    return ok()
