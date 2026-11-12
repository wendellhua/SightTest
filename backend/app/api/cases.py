"""用例路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.case import CaseCreate, CaseOut, CaseUpdate
from app.services import case as case_service

router = APIRouter(prefix="/projects/{project_id}/cases", tags=["cases"])


@router.get("")
async def list_cases(
    project_id: int,
    case_type: str | None = Query(None),
    version_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    total, items = await case_service.list_cases(
        db, user.id, project_id, user.is_admin, case_type, version_id, page, page_size
    )
    return ok(
        {
            "items": [CaseOut.model_validate(c) for c in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("")
async def create_case(
    project_id: int,
    data: CaseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await case_service.create_case(db, user.id, project_id, user.is_admin, data)
    return ok(CaseOut.model_validate(case))


@router.get("/{case_id}")
async def get_case(
    project_id: int,
    case_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await case_service.get_case(db, user.id, project_id, case_id, user.is_admin)
    return ok(CaseOut.model_validate(case))


@router.patch("/{case_id}")
async def update_case(
    project_id: int,
    case_id: int,
    data: CaseUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    case = await case_service.update_case(db, user.id, project_id, case_id, user.is_admin, data)
    return ok(CaseOut.model_validate(case))


@router.delete("/{case_id}")
async def delete_case(
    project_id: int,
    case_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await case_service.delete_case(db, user.id, project_id, case_id, user.is_admin)
    return ok()


@router.post("/{case_id}/debug")
async def debug_case(
    project_id: int,
    case_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    execution_id = await case_service.debug_case(db, user.id, project_id, case_id, user.is_admin)
    return ok({"execution_id": execution_id})
