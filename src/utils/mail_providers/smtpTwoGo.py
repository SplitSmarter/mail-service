import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException
from starlette import status

from src.config.config import SMTP2GO_ADMIN_USERNAME, smtp_two_go_admin_smtp_server, smtp_two_go_admin_smtp_port, \
    SMTP2GO_ADMIN_PASSWORD
from src.dto.base import ErrorResponse
from src.schemas.email_info import EmailInfo
from src.schemas.error_codes import ErrorCode, ErrorCodeMessage


def send_mail_smtp_two_go(
        subject: str,
        to: list[EmailInfo],
        from_: EmailInfo,
        logger: logging.Logger,
        html: str = "",
        text: str = "",
        cc: list[EmailInfo] = None,
        bcc: list[EmailInfo] = None
) -> bool:
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f'{from_.name} <{from_.email}>'
        message["To"] = ", ".join([f'{r.name} <{r.email}>' for r in to])
        if cc:
            message["Cc"] = ", ".join([f'{r.name} <{r.email}>' for r in cc])
        if text:
            message.attach(MIMEText(text, "plain"))
        if html:
            message.attach(MIMEText(html, "html"))

        all_recipients = [r.email for r in to]
        if cc:
            all_recipients += [r.email for r in cc]
        if bcc:
            all_recipients += [r.email for r in bcc]

        logger.debug(f"Sending mail via smtp2go smtp")

        server = smtplib.SMTP(smtp_two_go_admin_smtp_server, smtp_two_go_admin_smtp_port)
        server.starttls()
        server.login(SMTP2GO_ADMIN_USERNAME, SMTP2GO_ADMIN_PASSWORD)
        server.sendmail(from_.email, all_recipients, message.as_string())
        server.quit()
        logger.debug("Mail sent via smtp2go")
        return True
    except Exception as e:
        logger.exception("Error sending mail via smtp2go smtp")
        return False

