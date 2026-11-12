"""路由依赖：认证与当前用户。"""

import jwt as pyjwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.core.security import decode_access_token
from app.models import User
from app.services import account

_bearer = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> int:
    """解析 JWT，返回当前用户 id；未认证/凭证无效时抛业务异常。"""
    if credentials is None:
        raise AppException(ErrorCode.UNAUTHORIZED, "未登录")
    try:
        payload = decode_access_token(credentials.credentials)
    except pyjwt.PyJWTError:
        raise AppException(ErrorCode.INVALID_TOKEN, "登录凭证无效或已过期") from None
    return int(payload["sub"])


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """返回当前登录用户（含 is_admin，用于权限校验）；已冻结账号的旧 token 一并拒绝。"""
    user = await account.get_user(db, user_id)
    if user.status == "frozen":
        raise AppException(ErrorCode.FORBIDDEN, "账号已被冻结，请联系管理员")
    return user


async def get_active_user_id(user: User = Depends(get_current_user)) -> int:
    """返回已通过账号状态校验的当前用户 id。"""
    return user.id


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """校验当前用户为 admin，否则拒绝。"""
    if not user.is_admin:
        raise AppException(ErrorCode.FORBIDDEN, "需要管理员权限")
    return user
