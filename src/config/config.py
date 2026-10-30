import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Request

# Local/dev fallback only. Process env (Compose/K8s) wins — load_dotenv does not override.
_local_secrets = Path("mail_service_secrets.txt")
if _local_secrets.is_file():
    load_dotenv(_local_secrets)


default_email="info@splitsmarter.app"
default_email_name="Split Smarter"
gmail_smtp_server = "smtp.gmail.com"
gmail_smtp_port = 587
smtp_two_go_admin_smtp_server = "mail.smtp2go.com"
smtp_two_go_admin_smtp_port = 2525
elastic_mail_api_url = "https://api.elasticemail.com/v2/email/send"

TRACE_ID_HEADER_NAME = "X-Trace-Id"
USER_ID_HEADER_NAME = "X-User-Id"
AUTH_TOKEN_HEADER_NAME = "X-Auth-Token"
MAX_BODY_LOG_LENGTH = 500

APP_NAME = os.getenv("APP_NAME")
MAIL_DATABASE_URL=os.getenv("MAIL_DATABASE_URL")
ELASTIC_EMAIL_API_KEY=os.getenv("ELASTIC_EMAIL_API_KEY")
MAILERSEND_API_KEY=os.getenv("MAILERSEND_API_KEY")
GMAIL_APP_USER=os.getenv("GMAIL_APP_USER")
GMAIL_APP_PASSWORD=os.getenv("GMAIL_APP_PASSWORD")
SMTP2GO_ADMIN_USERNAME=os.getenv("SMTP2GO_ADMIN_USERNAME")
SMTP2GO_ADMIN_PASSWORD=os.getenv("SMTP2GO_ADMIN_PASSWORD")
NOTIFY_INBOX=os.getenv("NOTIFY_INBOX", default_email)
BREVO_API_KEY=os.getenv("BREVO_API_KEY")
brevo_api_url = "https://api.brevo.com/v3/smtp/email"


def _provider_enabled(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes"}


BREVO_ENABLED = _provider_enabled("BREVO_ENABLED", True)
SMTP2GO_ENABLED = _provider_enabled("SMTP2GO_ENABLED", False)
GMAIL_ENABLED = _provider_enabled("GMAIL_ENABLED", False)
ELASTIC_EMAIL_ENABLED = _provider_enabled("ELASTIC_EMAIL_ENABLED", False)
MAILERSEND_ENABLED = _provider_enabled("MAILERSEND_ENABLED", False)

# ==== Logging Config ====
TRACE_ID_KEY = "trace_id"
SERVICE_NAME = APP_NAME or "mail-service"


class JsonFormatter(logging.Formatter):
    """One JSON object per line for Alloy / Grafana Loki."""

    def format(self, record: logging.LogRecord) -> str:
        trace_id = getattr(record, TRACE_ID_KEY, None) or "-"
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "trace_id": trace_id,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


formatter = JsonFormatter()

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)

try:
    Path("logs").mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except OSError:
    pass

logger.propagate = False

class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Merge adapter context with extra kwargs
        extra = kwargs.get("extra", {})
        combined = {**self.extra, **extra}
        kwargs["extra"] = combined
        return msg, kwargs

def get_logger(trace_id: str | None = None, **context) -> logging.LoggerAdapter:
    extra = {TRACE_ID_KEY: trace_id or "-", **context}
    return ContextLoggerAdapter(logger, extra)

def get_request_logger(request: Request):
    trace_id = getattr(request.state, TRACE_ID_KEY, "N/A")
    return get_logger(trace_id)
