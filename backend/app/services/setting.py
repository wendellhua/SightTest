"""用户设置服务：探索限制、压测并发上限。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.models import PlatformSetting, UserSetting
from app.schemas.setting import SettingUpdate


async def get_setting(db: AsyncSession, user_id: int) -> UserSetting:
    """读取用户设置，不存在则按默认值初始化一行。"""
    setting = (await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))).scalar_one_or_none()
    if setting is None:
        setting = UserSetting(user_id=user_id)
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
    return setting


async def update_setting(db: AsyncSession, user_id: int, data: SettingUpdate) -> UserSetting:
    setting = await get_setting(db, user_id)
    platform = (await db.execute(select(PlatformSetting).where(PlatformSetting.id == 1))).scalar_one_or_none()
    payload = data.model_dump(exclude_unset=True)

    if "explore_minutes" in payload:
        limit = platform.default_explore_minutes if platform else 60
        if payload["explore_minutes"] > limit:
            raise AppException(ErrorCode.CONFLICT, f"探索时长不能超过平台上限 {limit} 分钟")
        setting.explore_minutes = payload["explore_minutes"]

    if "explore_pages" in payload:
        limit = platform.default_explore_pages if platform else 200
        if payload["explore_pages"] > limit:
            raise AppException(ErrorCode.CONFLICT, f"探索页面数不能超过平台上限 {limit} 页")
        setting.explore_pages = payload["explore_pages"]

    if "stress_limit" in payload:
        limit = platform.global_stress_limit if platform else 100
        if payload["stress_limit"] > limit:
            raise AppException(ErrorCode.CONFLICT, f"压测并发不能超过平台全局上限 {limit}")
        setting.stress_limit = payload["stress_limit"]

    if "account_stress_limit" in payload:
        setting.account_stress_limit = payload["account_stress_limit"]

    await db.commit()
    await db.refresh(setting)
    return setting
