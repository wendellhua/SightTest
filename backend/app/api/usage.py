"""用量与成本统计路由。"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.services import usage as usage_service

router = APIRouter(tags=["usage"])


@router.get("/usage")
async def get_usage(
    project_id: int | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return ok(await usage_service.get_usage(db, user.id, project_id, days))
