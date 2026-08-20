import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailNotConfiguredError(RuntimeError):
    pass


def smtp_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_from)


def send_email(*, to_email: str, subject: str, body_text: str) -> None:
    if not smtp_configured():
        raise EmailNotConfiguredError("SMTP no configurado")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body_text)

    context = ssl.create_default_context()
    if settings.smtp_secure:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context, timeout=30) as server:
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_pass)
            server.send_message(msg)
        return

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)


def send_welcome_email(*, to_email: str, name: str) -> None:
    base = (settings.app_public_url or "").rstrip("/")
    login_url = f"{base}/login" if base else "/login"
    subject = f"Acceso a {settings.app_name}"
    body = (
        f"Hola {name},\n\n"
        f"Ya tenés acceso al sistema {settings.app_name}.\n"
        f"Podés ingresar con este correo en: {login_url}\n\n"
        "Si no esperabas este mensaje, contactá al administrador.\n"
    )
    send_email(to_email=to_email, subject=subject, body_text=body)


def send_password_reset_email(*, to_email: str, name: str, raw_token: str) -> None:
    base = (settings.app_public_url or "").rstrip("/")
    if not base:
        raise EmailNotConfiguredError("APP_PUBLIC_URL no configurado")
    reset_url = f"{base}/reset-password?token={raw_token}"
    subject = f"Restablecer contraseña — {settings.app_name}"
    body = (
        f"Hola {name},\n\n"
        "Recibimos un pedido para restablecer tu contraseña.\n"
        f"Usá este enlace (válido por 1 hora, un solo uso):\n{reset_url}\n\n"
        "Si no pediste este cambio, ignorá este correo.\n"
    )
    send_email(to_email=to_email, subject=subject, body_text=body)
