"""ORM 模型集合，供 Alembic autogenerate 识别全部表。"""

from app.models.base import Base
from app.models.case import Case
from app.models.execution import CaseExecution, Execution, Issue, IssueCase, MisreportPattern
from app.models.model_call_log import ModelCallLog
from app.models.model_config import ModelConfig
from app.models.plan import PlanVersion
from app.models.platform import PlatformSetting
from app.models.project import Project, TestAccount
from app.models.report import Report
from app.models.user import EmailVerification, User, UserSetting

__all__ = [
    "Base",
    "User",
    "EmailVerification",
    "UserSetting",
    "ModelCallLog",
    "ModelConfig",
    "Project",
    "TestAccount",
    "PlanVersion",
    "Case",
    "Execution",
    "CaseExecution",
    "Issue",
    "IssueCase",
    "MisreportPattern",
    "Report",
    "PlatformSetting",
]
