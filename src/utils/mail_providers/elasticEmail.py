import logging

import requests

from src.config.config import ELASTIC_EMAIL_API_KEY, elastic_mail_api_url
from src.schemas.email_info import EmailInfo


def send_mail_elastic(
        subject: str,
        to: list[EmailInfo],
        from_: EmailInfo,
        logger: logging.Logger,
        html: str = "",
        text: str = "",
        cc: list[EmailInfo] = None,
        bcc: list[EmailInfo] = None
) -> dict:
    """
    Sends an email using Elastic Email HTTP API.
    Accepts consistent param structure across providers.
    """

    try:

        def extract_emails(addresses):
            return ",".join([d.email for d in addresses]) if addresses else ""

        payload = {
            "apikey": ELASTIC_EMAIL_API_KEY,
            "subject": subject,
            "from": from_.email,
            "fromName": from_.name,
            "to": extract_emails(to),
            "bodyHtml": html,
            "bodyText": text,
            "isTransactional": True
        }

        if cc:
            payload["cc"] = extract_emails(cc)
        if bcc:
            payload["bcc"] = extract_emails(bcc)



        logger.debug("Sending email via elastic mail API")
        response = requests.post(elastic_mail_api_url, data=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.debug("Email sent successfully via elastic mail API")
                return True
            else:
                logger.error(f"An error occurred while sending email via elastic mail API, response_received={result}")
                return False
        else:
            logger.error("Elastic email API returned HTTP Error")
            return False
    except Exception as e:
        logger.exception("Error sending mail via elastic mail API")
        return False
