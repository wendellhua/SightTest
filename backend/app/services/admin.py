"""admin 后台服务：用户、项目、平台设置管理。"""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.core.security import hash_password
from app.models import EmailVerification, ModelConfig, PlatformSetting, Project, User, UserSetting
from app.schemas.admin import AdminUserUpdate, PlatformSettingUpdate
from app.services.project import cascade_delete_project


async def list_users(
    db: AsyncSession, page: int, page_size: int, status: str | None
) -> tuple[int, list[User]]:
    filters = []
    if status:
        filters.append(User.status == status)
    total = (await db.execute(select(func.count()).select_from(User).where(*filters))).scalar_one()
    stmt = select(User).where(*filters).order_by(User.id).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def update_user(db: AsyncSession, user_id: int, data: AdminUserUpdate) -> User:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise AppException(ErrorCode.NOT_FOUND, "用户不存在")

    if data.status is not None:
        if user.is_admin:
            raise AppException(ErrorCode.CONFLICT, "不能修改 admin 账号状态")
        user.status = data.status
    if data.reset_password:
        user.password_hash = hash_password(data.reset_password)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int, current_user_id: int) -> None:
    if user_id == current_user_id:
        raise AppException(ErrorCode.FORBIDDEN, "不能删除自己")
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise AppException(ErrorCode.NOT_FOUND, "用户不存在")

    projects = list((await db.execute(select(Project).where(Project.creator_id == user_id))).scalars().all())
    for p in projects:
        await cascade_delete_project(db, p.id)

    await db.execute(delete(ModelConfig).where(ModelConfig.user_id == user_id))
    await db.execute(delete(UserSetting).where(UserSetting.user_id == user_id))
    await db.execute(delete(EmailVerification).where(EmailVerification.email == user.email))
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


async def list_projects(db: AsyncSession, page: int, page_size: int) -> tuple[int, list[Project]]:
    total = (await db.execute(select(func.count()).select_from(Project))).scalar_one()
    stmt = select(Project).order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def delete_project(db: AsyncSession, project_id: int) -> None:
    await cascade_delete_project(db, project_id)


async def get_platform_setting(db: AsyncSession) -> PlatformSetting:
    setting = (await db.execute(select(PlatformSetting).where(PlatformSetting.id == 1))).scalar_one_or_none()
    if setting is None:
        raise AppException(ErrorCode.NOT_FOUND, "平台设置不存在")
    return setting


async def update_platform_setting(db: AsyncSession, data: PlatformSettingUpdate) -> PlatformSetting:
    setting = await get_platform_setting(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    await db.commit()
    await db.refresh(setting)
    return setting
