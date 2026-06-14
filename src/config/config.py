import logging
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import Request

load_dotenv("mail_service_secrets.txt")

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

# ==== Logging Config ====
TRACE_ID_KEY = "trace_id"

class UTCFormatter(logging.Formatter):
    """Custom UTC formatter for consistent timestamps."""
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

LOG_FORMAT = "%(asctime)s - %(levelname)s - [trace_id=%(trace_id)s] - %(name)s - %(message)s"

formatter = UTCFormatter(LOG_FORMAT)

# Stream handler → stdout (container/docker friendly)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

# File handler (optional)
file_handler = logging.FileHandler("logs/mail-service.log")
file_handler.setFormatter(formatter)

# Application logger
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
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
