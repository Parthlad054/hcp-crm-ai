"""
auth/email.py — Async SMTP email helper for password-reset messages.
Uses aiosmtplib with STARTTLS (port 587).

Template rendering uses stdlib `string.Template` (dollar-sign placeholders)
so CSS braces in the HTML file are never misinterpreted by Python's str.format().
"""
import logging
import pathlib
import string
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)

# Resolved once at import time; raises FileNotFoundError early if missing.
_TEMPLATE_PATH = pathlib.Path(__file__).parent.parent / "templates" / "reset_password_email.html"

if not _TEMPLATE_PATH.exists():
    raise FileNotFoundError(
        f"Email template not found: {_TEMPLATE_PATH}. "
        "Ensure backend/app/templates/reset_password_email.html exists."
    )


def _render_html(otp: str, user_name: str) -> str:
    """
    Loads the HTML email template and substitutes $-delimited placeholders.

    Uses string.Template instead of str.format() so that CSS brace syntax
    (e.g. `body { font-family: ... }`) is never mistaken for format variables.

    Template variables expected in the file:
        $user_name      — recipient's display name
        $otp            — 6-digit one-time password
        $expire_minutes — token lifetime in minutes
    """
    raw = _TEMPLATE_PATH.read_text(encoding="utf-8")
    tpl = string.Template(raw)
    return tpl.substitute(
        user_name=user_name,
        otp=otp,
        expire_minutes=settings.RESET_TOKEN_EXPIRE_MINUTES,
    )


async def send_reset_email(to_email: str, user_name: str, otp: str) -> None:
    """
    Sends a password-reset OTP email via SMTP STARTTLS.
    Fires from a FastAPI BackgroundTask so it never blocks the response.

    Errors are logged with full tracebacks but never re-raised — the API
    has already returned 202 by the time this runs.
    """
    # ── Build message bodies ──────────────────────────────────────────────────
    try:
        html_body = _render_html(otp=otp, user_name=user_name)
    except (KeyError, ValueError) as exc:
        # KeyError   → a $placeholder in the template has no matching kwarg
        # ValueError → malformed placeholder — should never happen
        logger.error(
            "Template rendering failed for reset email to %s — %s: %s",
            to_email, type(exc).__name__, exc,
            exc_info=True,
        )
        return  # Cannot build HTML body; abort (202 already returned to client)

    plain_body = (
        f"Hi {user_name},\n\n"
        f"Your HCP CRM AI password reset code is: {otp}\n\n"
        f"Enter this 6-digit code in the app. It expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.\n\n"
        "If you didn't request a password reset, you can safely ignore this email.\n\n"
        "— HCP CRM AI"
    )

    # ── Assemble MIME message ─────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your HCP CRM AI password reset code"
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # ── Send via STARTTLS ─────────────────────────────────────────────────────
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("Password-reset OTP email sent to %s", to_email)
    except aiosmtplib.SMTPException as exc:
        # SMTP-level failure (auth error, connection refused, relay rejection…)
        logger.error(
            "SMTP error sending reset email to %s — %s: %s",
            to_email, type(exc).__name__, exc,
            exc_info=True,
        )
    except Exception as exc:
        # Catch-all for unexpected failures (DNS, TLS negotiation, etc.)
        logger.error(
            "Unexpected error sending reset email to %s — %s: %s",
            to_email, type(exc).__name__, exc,
            exc_info=True,
        )
