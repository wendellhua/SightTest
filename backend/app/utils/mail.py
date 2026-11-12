"""邮件发送能力。

注册验证、找回密码统一走此模块。SMTP 未配置或发送失败时抛出异常，
由调用方决定如何反馈给用户，绝不静默返回成功。
"""

import logging
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


class MailNotConfiguredError(RuntimeError):
    """SMTP 未配置，无法发送邮件。"""


class MailSendError(RuntimeError):
    """邮件发送失败（连接、认证或投递被拒）。"""


def _sender() -> str:
    sender = settings.smtp_from or settings.smtp_user
    if not sender:
        raise MailNotConfiguredError("SMTP_FROM 或 SMTP_USER 至少需配置一项")
    name, addr = parseaddr(sender)
    return formataddr((name or settings.app_name, addr))


async def send_mail(to: str, subject: str, body: str) -> None:
    """发送纯文本邮件；未配置或失败时抛出 MailNotConfiguredError / MailSendError。"""
    if not settings.smtp_host:
        raise MailNotConfiguredError("SMTP_HOST 未配置")

    message = EmailMessage()
    message["From"] = _sender()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    use_tls = settings.smtp_use_tls or settings.smtp_port == 465
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            use_tls=use_tls,
            start_tls=False if use_tls else settings.smtp_start_tls,
            timeout=settings.smtp_timeout,
        )
    except (aiosmtplib.SMTPException, OSError, TimeoutError) as exc:
        logger.error(
            "邮件发送失败 host=%s port=%s to=%s: %s: %s",
            settings.smtp_host, settings.smtp_port, to, type(exc).__name__, exc,
        )
        raise MailSendError(str(exc)) from exc
    logger.info("邮件已发送 to=%s subject=%s", to, subject)


async def send_verification_code(to: str, code: str, purpose: str) -> None:
    """发送邮箱验证码。"""
    subject = "【SightTest】邮箱验证码" if purpose == "register" else "【SightTest】找回密码验证码"
    body = f"您的验证码是 {code}，10 分钟内有效，请勿泄露。"
    await send_mail(to, subject, body)
