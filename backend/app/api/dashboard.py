"""平台首页与项目仪表盘路由。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.services import dashboard as dashboard_service

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def platform_home(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return ok(await dashboard_service.get_platform_home(db, user.id))


@router.get("/projects/{project_id}/dashboard")
async def project_dashboard(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return ok(await dashboard_service.get_project_dashboard(db, user.id, project_id, user.is_admin))
