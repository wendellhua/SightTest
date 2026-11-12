"""应用启动引导：确保内置管理员、平台设置等初始数据存在。"""

import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models import PlatformSetting, User

logger = logging.getLogger(__name__)


async def ensure_platform_setting() -> None:
    """确保平台设置单行记录（id=1）存在，后台「平台设置」与各类配额校验依赖该行。"""
    async with async_session_factory() as db:
        exists = (
            await db.execute(select(PlatformSetting.id).where(PlatformSetting.id == 1))
        ).scalar_one_or_none()
        if exists is not None:
            return
        db.add(PlatformSetting(id=1))
        await db.commit()
        logger.info("已初始化平台设置默认记录")


async def ensure_admin_user() -> None:
    """确保存在内置管理员账号（幂等，首次启动时自动创建）。

    默认账号密码来自配置项 `admin_email` / `admin_password`；
    若管理员邮箱已被普通用户占用，则跳过创建并记录告警。
    """
    admin_email = settings.admin_email.strip().lower()
    async with async_session_factory() as db:
        exists = (
            await db.execute(select(User.id).where(User.is_admin.is_(True)).limit(1))
        ).scalar_one_or_none()
        if exists is not None:
            return

        occupied = (
            await db.execute(select(User.id).where(User.email == admin_email))
        ).scalar_one_or_none()
        if occupied is not None:
            logger.warning("管理员邮箱 %s 已被普通用户占用，跳过创建", admin_email)
            return

        db.add(
            User(
                email=admin_email,
                password_hash=hash_password(settings.admin_password),
                name="平台管理员",
                is_admin=True,
            )
        )
        await db.commit()
        logger.info("已创建内置管理员账号 %s", admin_email)


async def bootstrap() -> None:
    """启动时执行的全部初始化。"""
    await ensure_platform_setting()
    await ensure_admin_user()
