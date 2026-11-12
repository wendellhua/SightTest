"""项目与测试账号路由。"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.project import (
    AccountIn,
    AccountOut,
    AccountUpdate,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    UrlCheckRequest,
)
from app.services import project as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/url-check")
async def url_check(data: UrlCheckRequest) -> dict[str, Any]:
    reachable = await project_service.check_url(data.url)
    return ok({"reachable": reachable})


@router.post("")
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    project = await project_service.create_project(db, user.id, data)
    return ok(ProjectOut.model_validate(project))


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    total, projects = await project_service.list_projects(db, user.id, page, page_size)
    return ok(
        {
            "items": [ProjectOut.model_validate(p) for p in projects],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    project = await project_service.get_project(db, user.id, project_id, user.is_admin)
    return ok(ProjectOut.model_validate(project))


@router.patch("/{project_id}")
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    project = await project_service.update_project(db, user.id, project_id, user.is_admin, data)
    return ok(ProjectOut.model_validate(project))


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await project_service.delete_project(db, user.id, project_id, user.is_admin)
    return ok()


@router.get("/{project_id}/accounts")
async def list_accounts(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    accounts = await project_service.list_accounts(db, user.id, project_id, user.is_admin)
    return ok([AccountOut.model_validate(a) for a in accounts])


@router.post("/{project_id}/accounts")
async def add_account(
    project_id: int,
    data: AccountIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    account = await project_service.add_account(db, user.id, project_id, user.is_admin, data)
    return ok(AccountOut.model_validate(account))


@router.patch("/{project_id}/accounts/{account_id}")
async def update_account(
    project_id: int,
    account_id: int,
    data: AccountUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    account = await project_service.update_account(db, user.id, project_id, account_id, user.is_admin, data)
    return ok(AccountOut.model_validate(account))


@router.delete("/{project_id}/accounts/{account_id}")
async def delete_account(
    project_id: int,
    account_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await project_service.delete_account(db, user.id, project_id, account_id, user.is_admin)
    return ok()
