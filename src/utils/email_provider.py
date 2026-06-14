import logging
import asyncio
import html2text
from fastapi import HTTPException
from mailersend import emails
from premailer import transform
from starlette import status

from src.config.config import MAILERSEND_API_KEY, default_email, default_email_name
from src.dto.base import ErrorResponse
from src.schemas.email_info import EmailInfo
from src.schemas.error_codes import ErrorCode, get_error_http_exception
from src.exceptions.custom_exceptions import MailError
from src.utils.mail_providers.elasticEmail import send_mail_elastic
from src.utils.mail_providers.googleMail import send_mail_gmail
from src.utils.mail_providers.mailerSend import send_mail_mailersend
from src.utils.mail_providers.smtpTwoGo import send_mail_smtp_two_go

mailer = emails.NewEmail(MAILERSEND_API_KEY)


def render_text_from_html(html: str) -> str:
    return html2text.html2text(html)


def inline_css(html: str) -> str:
    return transform(html)


async def send_email_provider(
        subject: str,
        to: list[EmailInfo],
        logger: logging.Logger,
        html: str = "",
        text: str = "",
        from_: EmailInfo = EmailInfo(email=default_email, name=default_email_name),
        cc: list[EmailInfo] | None = None,
        bcc: list[EmailInfo] | None = None,
) -> dict:
    """
    Attempts to send an email using multiple providers sequentially (Gmail, SMTP2Go, ElasticEmail, MailerSend),
    but without blocking the FastAPI event loop. Each provider runs in a separate thread via asyncio.to_thread().
    """

    try:
        html = inline_css(html)
        text = text or render_text_from_html(html)

        response = {"provider": None}

        # Helper to run sync senders in a non-blocking thread
        async def try_provider(func, provider_name: str):
            try:
                result = await asyncio.to_thread(
                    func,
                    subject=subject,
                    to=to,
                    html=html,
                    text=text,
                    from_=from_,
                    cc=cc,
                    bcc=bcc,
                    logger=logger,
                )
                if result:
                    response["provider"] = provider_name
                    logger.info(f"Email successfully sent using {provider_name}")
                    return True
            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}")
            return False

        # Sequentially try each provider (await keeps order, to_thread avoids blocking)
        if await try_provider(send_mail_smtp_two_go, "smtp2go"):
            return response

        if await try_provider(send_mail_gmail, "gmail"):
            return response

        if await try_provider(send_mail_elastic, "elastic_email"):
            return response

        if await try_provider(send_mail_mailersend, "mailersend"):
            return response

        logger.error("None of the providers were able to send an email")
        raise get_error_http_exception(ErrorCode.INTERNAL_SERVER)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error while sending email")
        raise get_error_http_exception(ErrorCode.INTERNAL_SERVER)
