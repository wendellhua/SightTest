"""应用配置。

统一从环境变量（或 `.env` 文件）读取，禁止在代码中硬编码凭证。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置项，字段名与 `.env` 保持一致。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SightTest"
    debug: bool = False

    # 数据库：async（FastAPI）与 sync（Alembic/Celery）分离
    database_url: str = "postgresql+asyncpg://sighttest:sighttest@localhost:5432/sighttest"
    database_url_sync: str = "postgresql+psycopg://sighttest:sighttest@localhost:5432/sighttest"

    # Redis：0=缓存/锁，1=broker，2=result
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret-key-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # 敏感信息加密（Fernet key）
    encryption_key: str = ""

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "sighttest"
    minio_secure: bool = False

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_start_tls: bool = True
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    # 内置管理员（应用首次启动时自动创建，建议首次登录后修改密码）
    admin_email: str = "admin@st.com"
    admin_password: str = "admin123"


@lru_cache
def get_settings() -> Settings:
    """返回单例配置对象。"""
    return Settings()


settings = get_settings()
