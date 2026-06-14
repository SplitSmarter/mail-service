import logging

from fastapi import HTTPException
from pydantic import EmailStr
from starlette import status

from src.dto.base import ErrorResponse
from src.schemas.email_info import EmailInfo
from src.schemas.error_codes import ErrorCode, ErrorCodeMessage
from src.utils.template_renderer import render_template
from src.utils.email_provider import send_email_provider


async def send_otp_email(
        otp: int,
        recipient: EmailStr,
        expiry_minutes: int,
        logger: logging.Logger,
        lang: str = "en"
) -> dict:
    """
    Sends a One-Time Password (OTP) email using language-aware template rendering and fallback email services.
    """
    try:
        context = {
            "otp": otp,
            "otp_expiry": expiry_minutes
        }

        html = render_template("send_otp.html", context, lang)

        return await send_email_provider(
            subject="OTP to Signup",
            to=[EmailInfo(email=recipient, name="User")],
            html=html,
            from_=EmailInfo(email="info@splitsmarter.app", name= "Split Smarter"),
            cc=None,
            bcc=None,
            logger=logger
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error while sending email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse[str, None](
                error=ErrorCode.INTERNAL_SERVER.value,
                message=ErrorCodeMessage.INTERNAL_SERVER.value,
            ).model_dump()
        )
