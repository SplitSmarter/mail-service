import logging

import requests

from src.config.config import BREVO_API_KEY, brevo_api_url
from src.schemas.email_info import EmailInfo


def _people(addresses: list[EmailInfo] | None) -> list[dict]:
    if not addresses:
        return []
    return [{"email": person.email, "name": person.name} for person in addresses]


def send_mail_brevo(
        subject: str,
        to: list[EmailInfo],
        from_: EmailInfo,
        logger: logging.Logger,
        html: str = "",
        text: str = "",
        cc: list[EmailInfo] | None = None,
        bcc: list[EmailInfo] | None = None,
) -> bool:
    if not BREVO_API_KEY:
        logger.error("Brevo API key is missing")
        return False
    payload = {
        "sender": {"email": from_.email, "name": from_.name},
        "to": _people(to),
        "subject": subject,
        "htmlContent": html,
        "textContent": text,
    }
    copied = _people(cc)
    if copied:
        payload["cc"] = copied
    hidden = _people(bcc)
    if hidden:
        payload["bcc"] = hidden
    try:
        response = requests.post(
            brevo_api_url,
            json=payload,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": BREVO_API_KEY,
            },
            timeout=20,
        )
    except Exception:
        logger.exception("Error sending mail via Brevo")
        return False
    if 200 <= response.status_code < 300:
        return True
    logger.error(
        "Brevo returned HTTP %s: %s",
        response.status_code,
        response.text[:300],
    )
    return False
