"""模型配置服务：CRUD 与连通性/图片识别检测。"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.core.security import decrypt_secret, encrypt_secret
from app.models import ModelConfig, Project
from app.schemas.model import ModelCreate, ModelUpdate
from app.utils.llm import ModelCheckResult, check_model


async def _get_owned_model(db: AsyncSession, user_id: int, model_id: int) -> ModelConfig:
    model = (await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))).scalar_one_or_none()
    if model is None:
        raise AppException(ErrorCode.NOT_FOUND, "模型配置不存在")
    if model.user_id != user_id:
        raise AppException(ErrorCode.FORBIDDEN, "无权操作该模型配置")
    return model


async def list_models(db: AsyncSession, user_id: int) -> list[ModelConfig]:
    stmt = select(ModelConfig).where(ModelConfig.user_id == user_id).order_by(ModelConfig.created_at.desc())
    return list((await db.execute(stmt)).scalars().all())


async def create_model(db: AsyncSession, user_id: int, data: ModelCreate) -> ModelConfig:
    result = await check_model(data.base_url, data.api_key, data.model)
    if not result.ok or not result.supports_vision:
        raise AppException(ErrorCode.CONFLICT, result.message)

    model = ModelConfig(
        user_id=user_id,
        name=data.name,
        base_url=data.base_url,
        api_key_encrypted=encrypt_secret(data.api_key),
        model=data.model,
        status="verified",
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


async def update_model(db: AsyncSession, user_id: int, model_id: int, data: ModelUpdate) -> ModelConfig:
    model = await _get_owned_model(db, user_id, model_id)
    payload = data.model_dump(exclude_unset=True)

    base_url = payload.get("base_url", model.base_url)
    new_model = payload.get("model", model.model)
    if payload.get("api_key") is not None:
        api_key_plain = payload["api_key"]
        model.api_key_encrypted = encrypt_secret(api_key_plain)
    else:
        api_key_plain = decrypt_secret(model.api_key_encrypted)

    result = await check_model(base_url, api_key_plain, new_model)
    if not result.ok or not result.supports_vision:
        raise AppException(ErrorCode.CONFLICT, result.message)

    if payload.get("name") is not None:
        model.name = payload["name"]
    if payload.get("base_url") is not None:
        model.base_url = payload["base_url"]
    if payload.get("model") is not None:
        model.model = payload["model"]
    model.status = "verified"
    await db.commit()
    await db.refresh(model)
    return model


async def delete_model(db: AsyncSession, user_id: int, model_id: int) -> None:
    model = await _get_owned_model(db, user_id, model_id)
    bound = (
        await db.execute(select(Project.id).where(Project.model_config_id == model_id).limit(1))
    ).scalar_one_or_none()
    if bound is not None:
        raise AppException(ErrorCode.CONFLICT, "该模型已被项目绑定，无法删除")
    await db.execute(delete(ModelConfig).where(ModelConfig.id == model_id))
    await db.commit()


async def test_model(db: AsyncSession, user_id: int, model_id: int) -> ModelCheckResult:
    model = await _get_owned_model(db, user_id, model_id)
    api_key = decrypt_secret(model.api_key_encrypted)
    return await check_model(model.base_url, api_key, model.model)
