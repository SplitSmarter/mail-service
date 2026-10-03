import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config.config import (GMAIL_APP_USER,
                               GMAIL_APP_PASSWORD, gmail_smtp_server, gmail_smtp_port)
from src.schemas.email_info import EmailInfo


def send_mail_gmail(
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

        logger.debug(
            f"Sending mail via gmail smtp, "
            f"to={message['To']}, from={message['From']}, "
            f"recipients={all_recipients}, "
            f"server_host={gmail_smtp_server}, server_port={gmail_smtp_port}"
        )

        server = smtplib.SMTP(gmail_smtp_server, gmail_smtp_port)
        server.starttls()
        server.login(GMAIL_APP_USER, GMAIL_APP_PASSWORD)

        logger.debug(f"Logged in to gmail smtp")

        server.sendmail(from_.email, all_recipients, message.as_string())
        server.quit()

        logger.debug("Mail sent via gmail")

        return True
    except Exception as e:
        logger.exception("Error sending mail via gmail smtp")
        return False
