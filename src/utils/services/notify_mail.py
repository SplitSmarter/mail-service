import logging
import re

from fastapi import HTTPException
from starlette import status

from src.config.config import NOTIFY_INBOX, default_email, default_email_name
from src.dto.base import ErrorResponse
from src.schemas.email_info import EmailInfo
from src.schemas.error_codes import ErrorCode, ErrorCodeMessage
from src.utils.email_provider import send_email_provider
from src.utils.template_renderer import render_template

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class InvalidNotifyContact(ValueError):
    pass


def normalize_notify_contact(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if "@" in text:
        email = text.lower()
        if not _EMAIL.fullmatch(email) or len(email) > 254:
            raise InvalidNotifyContact("Enter an email or phone number.")
        return email, "email"
    compact = re.sub(r"[\s().-]", "", text)
    digits = compact[1:] if compact.startswith("+") else compact
    if not digits.isdigit() or not 8 <= len(digits) <= 15:
        raise InvalidNotifyContact("Enter an email or phone number.")
    return f"+{digits}", "phone"


def notify_inbox() -> str:
    inbox = (NOTIFY_INBOX or default_email).strip()
    return inbox or default_email


async def send_notify_mail(contact: str, logger: logging.Logger) -> dict:
    try:
        normalized, kind = normalize_notify_contact(contact)
    except InvalidNotifyContact as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        html = render_template(
            "notify.html",
            {"contact": normalized, "kind": kind},
            "en",
        )
        response = await send_email_provider(
            subject="New notify request",
            to=[EmailInfo(email=notify_inbox(), name=default_email_name)],
            html=html,
            logger=logger,
        )
        return {"provider": response.get("provider"), "kind": kind}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error while sending notify mail")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse[str, None](
                error=ErrorCode.INTERNAL_SERVER.value,
                message=ErrorCodeMessage.INTERNAL_SERVER.value,
            ).model_dump(),
        )
