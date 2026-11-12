"""邮件发送能力。

注册验证、找回密码、任务完成通知统一走此模块。SMTP 未配置时（开发环境）
不真正发送，仅在 debug 模式下记录内容，便于本地联调。
"""

import logging

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_mail(to: str, subject: str, body: str) -> None:
    """发送纯文本邮件。"""
    if not settings.smtp_host:
        if settings.debug:
            logger.info("开发模式（SMTP 未配置）不发送邮件。收件人=%s 主题=%s 内容=%s", to, subject, body)
        return

    message = aiosmtplib.email.message.EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=True,
    )


async def send_verification_code(to: str, code: str, purpose: str) -> None:
    """发送邮箱验证码。"""
    subject = "【SightTest】邮箱验证码" if purpose == "register" else "【SightTest】找回密码验证码"
    body = f"您的验证码是 {code}，10 分钟内有效，请勿泄露。"
    await send_mail(to, subject, body)
