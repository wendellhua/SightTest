"""账号服务：注册、登录、验证码、找回密码、改密、注销。

业务规则（归属、状态、配额）在此层校验，路由层不承载业务逻辑。
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.core.security import create_access_token, hash_password, verify_password
from app.models import EmailVerification, User, UserSetting
from app.schemas.auth import (
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from app.utils.mail import MailNotConfiguredError, MailSendError, send_verification_code

logger = logging.getLogger(__name__)

CODE_TTL = timedelta(minutes=10)
RESEND_INTERVAL = timedelta(seconds=60)
MAX_CODE_ATTEMPTS = 5


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _now() -> datetime:
    return datetime.now(UTC)


async def send_code(db: AsyncSession, email: str, purpose: str) -> None:
    """发送验证码，同邮箱同用途 60 秒内限发一次。

    邮件真正投递成功后才落库；发送失败会回滚并返回明确错误，不占用限流窗口。
    """
    registered = (await db.execute(select(User.id).where(User.email == email))).scalar_one_or_none()
    if purpose == "register" and registered is not None:
        raise AppException(ErrorCode.CONFLICT, "该邮箱已注册，请直接登录")
    if purpose == "reset_password" and registered is None:
        raise AppException(ErrorCode.NOT_FOUND, "该邮箱未注册")

    stmt = (
        select(EmailVerification)
        .where(EmailVerification.email == email, EmailVerification.purpose == purpose)
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    last = (await db.execute(stmt)).scalar_one_or_none()
    if last is not None and _now() - last.created_at < RESEND_INTERVAL:
        raise AppException(ErrorCode.TOO_MANY_REQUESTS, "验证码发送过于频繁，请稍后再试")

    record = EmailVerification(
        email=email,
        code=_generate_code(),
        purpose=purpose,
        expires_at=_now() + CODE_TTL,
    )
    db.add(record)
    await db.flush()
    try:
        await send_verification_code(email, record.code, purpose)
    except MailNotConfiguredError as exc:
        await db.rollback()
        logger.error("邮件服务未配置，无法发送验证码: %s", exc)
        raise AppException(ErrorCode.SERVICE_UNAVAILABLE, "邮件服务未配置，暂时无法发送验证码，请联系管理员") from None
    except MailSendError:
        await db.rollback()
        raise AppException(ErrorCode.SERVICE_UNAVAILABLE, "验证码邮件发送失败，请检查邮箱地址或稍后重试") from None
    await db.commit()


async def _consume_code(db: AsyncSession, email: str, purpose: str, code: str) -> None:
    """校验并核销验证码（单次有效，错误次数超限即作废）。

    校验成功时仅标记已使用，由调用方在同一事务中提交，保证与业务写入原子性。
    """
    stmt = (
        select(EmailVerification)
        .where(
            EmailVerification.email == email,
            EmailVerification.purpose == purpose,
            EmailVerification.used.is_(False),
        )
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    record = (await db.execute(stmt)).scalar_one_or_none()
    if record is None:
        raise AppException(ErrorCode.VALIDATION_ERROR, "验证码错误或已失效，请重新获取")
    if record.expires_at < _now():
        raise AppException(ErrorCode.VALIDATION_ERROR, "验证码已过期，请重新获取")
    if not secrets.compare_digest(record.code, code):
        record.failed_attempts += 1
        exhausted = record.failed_attempts >= MAX_CODE_ATTEMPTS
        if exhausted:
            record.used = True
        await db.commit()
        if exhausted:
            raise AppException(ErrorCode.VALIDATION_ERROR, "验证码错误次数过多，请重新获取")
        raise AppException(ErrorCode.VALIDATION_ERROR, "验证码错误")
    record.used = True


async def register(db: AsyncSession, data: RegisterRequest) -> TokenResponse:
    """注册即登录，返回 token。"""
    exists = (await db.execute(select(User.id).where(User.email == data.email))).scalar_one_or_none()
    if exists is not None:
        raise AppException(ErrorCode.CONFLICT, "该邮箱已注册")

    await _consume_code(db, data.email, "register", data.code)

    user = User(email=data.email, password_hash=hash_password(data.password), name=data.name)
    db.add(user)
    try:
        await db.flush()
        db.add(UserSetting(user_id=user.id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppException(ErrorCode.CONFLICT, "该邮箱已注册") from None
    await db.refresh(user)
    return TokenResponse(token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    """登录。"""
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        raise AppException(ErrorCode.UNAUTHORIZED, "邮箱或密码错误")
    if user.status == "frozen":
        raise AppException(ErrorCode.FORBIDDEN, "账号已被冻结，请联系管理员")
    return TokenResponse(token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


async def reset_password(db: AsyncSession, data: ResetPasswordRequest) -> None:
    """找回密码。"""
    user = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if user is None:
        raise AppException(ErrorCode.NOT_FOUND, "该邮箱未注册")
    await _consume_code(db, data.email, "reset_password", data.code)
    user.password_hash = hash_password(data.new_password)
    await db.commit()


async def get_user(db: AsyncSession, user_id: int) -> User:
    """按 id 查询用户。"""
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise AppException(ErrorCode.NOT_FOUND, "用户不存在")
    return user


async def update_profile(db: AsyncSession, user_id: int, name: str) -> User:
    """更新个人资料。"""
    user = await get_user(db, user_id)
    user.name = name
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> None:
    """修改登录密码。"""
    user = await get_user(db, user_id)
    if not verify_password(old_password, user.password_hash):
        raise AppException(ErrorCode.VALIDATION_ERROR, "原密码错误")
    user.password_hash = hash_password(new_password)
    user.admin_password_changed = True
    await db.commit()


async def request_cancel(db: AsyncSession, user_id: int) -> None:
    """申请注销，进入 7 天冷静期。"""
    user = await get_user(db, user_id)
    if user.is_admin:
        raise AppException(ErrorCode.FORBIDDEN, "管理员账号不可注销")
    user.status = "cancelling"
    user.cancellation_requested_at = _now()
    await db.commit()


async def revoke_cancel(db: AsyncSession, user_id: int) -> None:
    """撤销注销申请。"""
    user = await get_user(db, user_id)
    if user.status != "cancelling":
        raise AppException(ErrorCode.CONFLICT, "当前不在注销冷静期内")
    user.status = "normal"
    user.cancellation_requested_at = None
    await db.commit()
