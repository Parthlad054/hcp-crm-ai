"""
auth/email.py — Async SMTP email helper for password-reset messages.
Uses aiosmtplib with STARTTLS (port 587).
"""
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)

# The frontend URL where the reset form lives
FRONTEND_RESET_URL = "http://localhost:5173/reset-password"


async def send_reset_email(to_email: str, user_name: str, reset_token: str) -> None:
    """
    Sends a password-reset email via SMTP STARTTLS.
    Fires from a FastAPI BackgroundTask so it never blocks the response.
    """
    reset_link = f"{FRONTEND_RESET_URL}?token={reset_token}"

    # ── Build the HTML message ────────────────────────────────────────────────
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .card {{ max-width: 520px; margin: 40px auto; background: #ffffff; border-radius: 12px;
                 padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        h2 {{ color: #1e293b; margin-top: 0; }}
        p  {{ color: #475569; line-height: 1.6; }}
        .btn {{ display: inline-block; margin: 24px 0; padding: 13px 28px;
                background: #2563eb; color: #ffffff !important; text-decoration: none;
                border-radius: 8px; font-weight: 600; font-size: 15px; }}
        .note {{ font-size: 13px; color: #94a3b8; margin-top: 24px; }}
        .logo {{ font-size: 22px; font-weight: 700; color: #2563eb; margin-bottom: 24px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">⚕️ HCP CRM AI</div>
        <h2>Reset your password</h2>
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>We received a request to reset the password for your HCP CRM AI account.
           Click the button below to choose a new password.</p>
        <a class="btn" href="{reset_link}">Reset Password</a>
        <p>This link expires in <strong>{settings.RESET_TOKEN_EXPIRE_MINUTES} minutes</strong>.
           If you didn't request a password reset, you can safely ignore this email.</p>
        <p class="note">
          If the button doesn't work, paste this URL into your browser:<br/>
          <a href="{reset_link}">{reset_link}</a>
        </p>
      </div>
    </body>
    </html>
    """

    plain_body = (
        f"Hi {user_name},\n\n"
        "We received a request to reset your HCP CRM AI password.\n\n"
        f"Click the link below to reset it (expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes):\n"
        f"{reset_link}\n\n"
        "If you didn't request this, please ignore this email."
    )

    # ── Assemble MIME message ─────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your HCP CRM AI password"
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
        logger.info("Password-reset email sent to %s", to_email)
    except Exception as exc:
        # Log but don't bubble up — the API already returned 202
        logger.error("Failed to send reset email to %s: %s", to_email, exc)
