"""方案建设路由。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.build import BuildStartRequest, VersionDetailOut, VersionOut
from app.services import build as build_service

router = APIRouter(prefix="/projects/{project_id}", tags=["builds"])


@router.post("/builds")
async def start_build(
    project_id: int,
    data: BuildStartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    build_id = await build_service.start_build(db, user.id, project_id, user.is_admin, data)
    return ok({"build_id": build_id})


@router.get("/builds/{build_id}")
async def get_build(
    project_id: int,
    build_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    build = await build_service.get_build(db, user.id, project_id, build_id, user.is_admin)
    return ok(build)


@router.post("/builds/{build_id}/terminate")
async def terminate_build(
    project_id: int,
    build_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await build_service.terminate_build(db, user.id, project_id, build_id, user.is_admin)
    return ok()


@router.get("/versions")
async def list_versions(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    versions = await build_service.list_versions(db, user.id, project_id, user.is_admin)
    return ok([VersionOut.model_validate(v) for v in versions])


@router.get("/versions/{version_id}")
async def get_version(
    project_id: int,
    version_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    version = await build_service.get_version(db, user.id, project_id, version_id, user.is_admin)
    return ok(VersionDetailOut.model_validate(version))
