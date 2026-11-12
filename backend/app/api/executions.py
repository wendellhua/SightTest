"""测试执行、问题与误报清单路由。"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.execution import (
    CaseExecutionOut,
    ExecutionCreate,
    ExecutionOut,
    IssueOut,
    IssueUpdate,
    MisreportPatternOut,
    MisreportPatternUpdate,
)
from app.services import execution as execution_service

router = APIRouter(prefix="/projects/{project_id}", tags=["executions"])


@router.post("/executions")
async def start_execution(
    project_id: int,
    data: ExecutionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    execution_id = await execution_service.start_execution(db, user.id, project_id, user.is_admin, data)
    return ok({"execution_id": execution_id})


@router.get("/executions")
async def list_executions(
    project_id: int,
    include_debug: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    total, items = await execution_service.list_executions(
        db, user.id, project_id, user.is_admin, include_debug, page, page_size
    )
    return ok(
        {
            "items": [ExecutionOut.model_validate(e) for e in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/executions/{execution_id}")
async def get_execution(
    project_id: int,
    execution_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    execution = await execution_service.get_execution(db, user.id, project_id, execution_id, user.is_admin)
    return ok(ExecutionOut.model_validate(execution))


@router.post("/executions/{execution_id}/terminate")
async def terminate_execution(
    project_id: int,
    execution_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await execution_service.terminate_execution(db, user.id, project_id, execution_id, user.is_admin)
    return ok()


@router.get("/executions/{execution_id}/cases")
async def list_case_executions(
    project_id: int,
    execution_id: int,
    result: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    items = await execution_service.list_case_executions(
        db, user.id, project_id, execution_id, user.is_admin, result
    )
    return ok([CaseExecutionOut.model_validate(c) for c in items])


@router.get("/issues")
async def list_issues(
    project_id: int,
    severity: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    total, items = await execution_service.list_issues(
        db, user.id, project_id, user.is_admin, severity, page, page_size
    )
    return ok(
        {
            "items": [IssueOut.model_validate(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.patch("/issues/{issue_id}")
async def update_issue(
    project_id: int,
    issue_id: int,
    data: IssueUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    issue = await execution_service.update_issue(db, user.id, project_id, issue_id, user.is_admin, data)
    return ok(IssueOut.model_validate(issue))


@router.get("/misreport-patterns")
async def list_misreport_patterns(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    patterns = await execution_service.list_misreport_patterns(db, user.id, project_id, user.is_admin)
    return ok([MisreportPatternOut.model_validate(p) for p in patterns])


@router.patch("/misreport-patterns/{pattern_id}")
async def update_misreport_pattern(
    project_id: int,
    pattern_id: int,
    data: MisreportPatternUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    pattern = await execution_service.update_misreport_pattern(
        db, user.id, project_id, pattern_id, user.is_admin, data
    )
    return ok(MisreportPatternOut.model_validate(pattern))


@router.get("/perf-trends")
async def get_perf_trends(
    project_id: int,
    case_id: int = Query(...),
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    trends = await execution_service.get_perf_trends(db, user.id, project_id, user.is_admin, case_id, days)
    return ok(trends)
