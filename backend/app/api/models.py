"""模型配置路由。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models import User
from app.schemas.model import ModelCreate, ModelOut, ModelUpdate
from app.services import model as model_service

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    models = await model_service.list_models(db, user.id)
    return ok([ModelOut.model_validate(m) for m in models])


@router.post("")
async def create_model(
    data: ModelCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    model = await model_service.create_model(db, user.id, data)
    return ok(ModelOut.model_validate(model))


@router.patch("/{model_id}")
async def update_model(
    model_id: int,
    data: ModelUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    model = await model_service.update_model(db, user.id, model_id, data)
    return ok(ModelOut.model_validate(model))


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await model_service.delete_model(db, user.id, model_id)
    return ok()


@router.post("/{model_id}/test")
async def test_model(
    model_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await model_service.test_model(db, user.id, model_id)
    return ok({"ok": result.ok, "supports_vision": result.supports_vision, "message": result.message})
