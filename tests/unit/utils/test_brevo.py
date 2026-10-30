from unittest.mock import MagicMock, patch

import pytest

from src.schemas.email_info import EmailInfo
from src.utils.mail_providers.brevo import send_mail_brevo

pytestmark = pytest.mark.unit


def test_send_mail_brevo_posts_the_message(logger):
    response = MagicMock(status_code=201, text="")
    to = [EmailInfo(email="user@example.com", name="User")]
    sender = EmailInfo(email="info@splitsmarter.app", name="Split Smarter")

    with (
        patch("src.utils.mail_providers.brevo.BREVO_API_KEY", "test-key"),
        patch("src.utils.mail_providers.brevo.requests.post", return_value=response) as post,
    ):
        sent = send_mail_brevo(
            subject="Hello",
            to=to,
            from_=sender,
            html="<p>hi</p>",
            text="hi",
            logger=logger,
        )

    assert sent is True
    payload = post.call_args.kwargs["json"]
    assert post.call_args.kwargs["headers"]["api-key"] == "test-key"
    assert payload["sender"]["email"] == "info@splitsmarter.app"
    assert payload["to"] == [{"email": "user@example.com", "name": "User"}]
    assert payload["subject"] == "Hello"


def test_send_mail_brevo_returns_false_on_http_error(logger):
    response = MagicMock(status_code=401, text="unauthorized")
    to = [EmailInfo(email="user@example.com", name="User")]
    sender = EmailInfo(email="info@splitsmarter.app", name="Split Smarter")

    with (
        patch("src.utils.mail_providers.brevo.BREVO_API_KEY", "test-key"),
        patch("src.utils.mail_providers.brevo.requests.post", return_value=response),
    ):
        sent = send_mail_brevo(
            subject="Hello",
            to=to,
            from_=sender,
            logger=logger,
        )

    assert sent is False
