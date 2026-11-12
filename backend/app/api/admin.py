"""admin 后台路由。"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.admin import (
    AdminProjectOut,
    AdminUserOut,
    AdminUserUpdate,
    PlatformSettingOut,
    PlatformSettingUpdate,
)
from app.services import admin as admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    total, items = await admin_service.list_users(db, page, page_size, status)
    return ok(
        {
            "items": [AdminUserOut.model_validate(u) for u in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    data: AdminUserUpdate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user = await admin_service.update_user(db, user_id, data)
    return ok(AdminUserOut.model_validate(user))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await admin_service.delete_user(db, user_id, admin.id)
    return ok()


@router.get("/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    total, items = await admin_service.list_projects(db, page, page_size)
    return ok(
        {
            "items": [AdminProjectOut.model_validate(p) for p in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await admin_service.delete_project(db, project_id)
    return ok()


@router.get("/settings")
async def get_settings(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    setting = await admin_service.get_platform_setting(db)
    return ok(PlatformSettingOut.model_validate(setting))


@router.patch("/settings")
async def update_settings(
    data: PlatformSettingUpdate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    setting = await admin_service.update_platform_setting(db, data)
    return ok(PlatformSettingOut.model_validate(setting))
