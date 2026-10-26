from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from src.utils.services.otp_mail import send_otp_email

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_send_otp_email_renders_and_delegates_to_provider(logger):
    with (
        patch(
            "src.utils.services.otp_mail.render_template",
            return_value="<p>654321</p>",
        ) as render,
        patch(
            "src.utils.services.otp_mail.send_email_provider",
            new_callable=AsyncMock,
            return_value={"provider": "gmail"},
        ) as send_provider,
    ):
        result = await send_otp_email(
            otp=654321,
            recipient="user@example.com",
            expiry_minutes=10,
            logger=logger,
        )

    assert result == {"provider": "gmail"}
    render.assert_called_once_with(
        "send_otp.html",
        {"otp": 654321, "otp_expiry": 10},
        "en",
    )
    send_provider.assert_awaited_once()
    kwargs = send_provider.await_args.kwargs
    assert kwargs["subject"] == "OTP to Signup"
    assert kwargs["html"] == "<p>654321</p>"
    assert kwargs["to"][0].email == "user@example.com"


@pytest.mark.asyncio
async def test_send_otp_email_rethrows_http_exception(logger):
    with (
        patch(
            "src.utils.services.otp_mail.render_template",
            return_value="<p>1</p>",
        ),
        patch(
            "src.utils.services.otp_mail.send_email_provider",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=500, detail="boom"),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await send_otp_email(
                otp=1,
                recipient="user@example.com",
                expiry_minutes=5,
                logger=logger,
            )

    assert exc_info.value.status_code == 500
