"""用户路由：个人信息、改密、注销。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.core.response import ok
from app.schemas.auth import ChangePasswordRequest, UpdateProfileRequest, UserOut
from app.services import account

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    user = await account.get_user(db, user_id)
    return ok(UserOut.model_validate(user))


@router.patch("/me")
async def update_me(
    data: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user = await account.update_profile(db, user_id, data.name)
    return ok(UserOut.model_validate(user))


@router.patch("/me/password")
async def change_password(
    data: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await account.change_password(db, user_id, data.old_password, data.new_password)
    return ok()


@router.post("/me/cancel")
async def request_cancel(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    await account.request_cancel(db, user_id)
    return ok()


@router.post("/me/cancel/revoke")
async def revoke_cancel(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    await account.revoke_cancel(db, user_id)
    return ok()
