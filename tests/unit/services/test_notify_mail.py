from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from src.utils.services.notify_mail import normalize_notify_contact, send_notify_mail

pytestmark = pytest.mark.unit


def test_normalize_email_and_phone():
    assert normalize_notify_contact("  Ada@Example.com ") == ("ada@example.com", "email")
    assert normalize_notify_contact("+1 (415) 555-0134") == ("+14155550134", "phone")


@pytest.mark.asyncio
async def test_send_goes_to_the_configured_inbox(logger):
    with (
        patch("src.utils.services.notify_mail.notify_inbox", return_value="inbox@splitsmarter.app"),
        patch(
            "src.utils.services.notify_mail.render_template",
            return_value="<p>notify</p>",
        ),
        patch(
            "src.utils.services.notify_mail.send_email_provider",
            new_callable=AsyncMock,
            return_value={"provider": "smtp2go"},
        ) as send_provider,
    ):
        result = await send_notify_mail("Ada@Example.com", logger)

    assert result == {"provider": "smtp2go", "kind": "email"}
    sent_to = send_provider.await_args.kwargs["to"]
    assert sent_to[0].email == "inbox@splitsmarter.app"
    assert send_provider.await_args.kwargs["subject"] == "New notify request"


@pytest.mark.asyncio
async def test_send_rejects_a_name(logger):
    with pytest.raises(HTTPException) as raised:
        await send_notify_mail("Ada Lovelace", logger)
    assert raised.value.status_code == 400
