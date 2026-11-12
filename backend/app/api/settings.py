"""用户设置路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.setting import SettingOut, SettingUpdate
from app.services import setting as setting_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
async def get_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    setting = await setting_service.get_setting(db, user.id)
    return ok(SettingOut.model_validate(setting))


@router.patch("")
async def update_settings(
    data: SettingUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    setting = await setting_service.update_setting(db, user.id, data)
    return ok(SettingOut.model_validate(setting))
