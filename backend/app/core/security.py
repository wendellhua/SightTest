"""安全能力：JWT 签发/校验、敏感信息对称加密。

- JWT 用于登录凭证；测试账号密码与 API Key 用 Fernet 对称加密（可逆，用于回放登录/调用模型）。
- 加密密钥缺失时抛出异常，禁止明文落库。
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    """签发 JWT，subject 为用户 id。"""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """校验并解析 JWT，失败抛 jwt.PyJWTError。"""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def _fernet() -> Fernet:
    if not settings.encryption_key:
        raise RuntimeError("ENCRYPTION_KEY 未配置，无法进行敏感信息加解密")
    return Fernet(settings.encryption_key.encode())


def encrypt_secret(plain: str) -> str:
    """加密敏感信息（测试账号密码、API Key），返回密文字符串。"""
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_secret(cipher: str) -> str:
    """解密敏感信息，密文无效时抛 InvalidToken。"""
    try:
        return _fernet().decrypt(cipher.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("敏感信息解密失败，密钥可能已变更") from exc


def hash_password(password: str) -> str:
    """生成登录密码哈希（PBKDF2-SHA256 + 随机盐）。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, hashed: str) -> bool:
    """校验登录密码。"""
    try:
        salt, digest = hashed.split("$", 1)
    except ValueError:
        return False
    computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return secrets.compare_digest(computed, digest)
