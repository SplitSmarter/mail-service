import json

from mailersend import emails
import logging

from src.config.config import MAILERSEND_API_KEY
from src.schemas.email_info import EmailInfo

mailer = emails.NewEmail(MAILERSEND_API_KEY)


def send_mail_mailersend(
    subject: str,
    to: list[EmailInfo],
    from_: EmailInfo,
    logger: logging.Logger,
    html: str = "",
    text: str = "",
    cc: list[EmailInfo] = None,
    bcc: list[EmailInfo] = None
) -> bool:
    """
    Sends an email using MailerSend.
    """

    try:
        mail_body = {}

        # Convert EmailInfo objects -> dicts
        to_list = [{"email": t.email, "name": t.name} for t in to]
        from_dict = {"email": from_.email, "name": from_.name} if from_ else None
        cc_list = [{"email": c.email, "name": c.name} for c in cc] if cc else []
        bcc_list = [{"email": b.email, "name": b.name} for b in bcc] if bcc else []

        mailer.set_subject(subject, mail_body)
        mailer.set_mail_to(to_list, mail_body)

        if from_dict:
            mailer.set_mail_from(from_dict, mail_body)
        if html:
            mailer.set_html_content(html, mail_body)
        if text:
            mailer.set_plaintext_content(text, mail_body)
        if cc_list:
            mailer.set_cc_recipients(cc_list, mail_body)
        if bcc_list:
            mailer.set_bcc_recipients(bcc_list, mail_body)

        logger.debug(
            f"Sending email via MailerSend, to={to_list}, from={from_dict}, cc={cc_list}, bcc={bcc_list}"
        )
        response_str = mailer.send(mail_body)
        logger.debug(f"Raw MailerSend response: {response_str}")

        status_code = None
        body_text = None

        try:
            lines = response_str.strip().split("\n", 1)
            status_code = int(lines[0].strip())
            body_text = lines[1].strip() if len(lines) > 1 else ""
        except Exception:
            logger.warning(f"Unexpected MailerSend response format: {response_str}")

        # Parse JSON body if possible
        json_body = {}
        if body_text:
            try:
                json_body = json.loads(body_text)
            except json.JSONDecodeError:
                json_body = {"message": body_text}

        # --- Evaluate Response ---
        if status_code in (200, 202):
            logger.info(f"Mail sent successfully via MailerSend, status_code={status_code}")
            return True
        else:
            logger.error(
                f"MailerSend API returned error. status_code={status_code}, response={json_body}"
            )
            return False

    except Exception as e:
        logger.exception("Error sending mail via mailersend")
        return False
