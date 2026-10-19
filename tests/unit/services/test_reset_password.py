from unittest.mock import AsyncMock, patch

import pytest

from src.utils.services.reset_password import send_reset_password_email

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_send_reset_password_email_renders_and_delegates(logger):
    link = "https://app.example.com/reset?token=xyz"

    with (
        patch(
            "src.utils.services.reset_password.render_template",
            return_value="<p>reset</p>",
        ) as render,
        patch(
            "src.utils.services.reset_password.send_email_provider",
            new_callable=AsyncMock,
            return_value={"provider": "smtp2go"},
        ) as send_provider,
    ):
        result = await send_reset_password_email(
            reset_link=link,
            recipient="user@example.com",
            logger=logger,
        )

    assert result == {"provider": "smtp2go"}
    render.assert_called_once_with(
        "reset_password.html",
        {"reset_link": link},
        "en",
    )
    send_provider.assert_awaited_once()
    assert send_provider.await_args.kwargs["subject"] == "Reset Your Password"
