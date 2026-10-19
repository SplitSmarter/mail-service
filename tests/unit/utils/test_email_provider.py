from unittest.mock import patch

import pytest
from fastapi import HTTPException

from src.schemas.email_info import EmailInfo
from src.utils.email_provider import render_text_from_html, send_email_provider

pytestmark = pytest.mark.unit


def test_render_text_from_html_strips_tags():
    text = render_text_from_html("<p>Hello <b>world</b></p>")
    assert "Hello" in text
    assert "world" in text
    assert "<p>" not in text


@pytest.mark.asyncio
async def test_send_email_provider_returns_first_successful_provider(logger):
    to = [EmailInfo(email="user@example.com", name="User")]

    with (
        patch("src.utils.email_provider.inline_css", return_value="<p>hi</p>"),
        patch("src.utils.email_provider.render_text_from_html", return_value="hi"),
        patch("src.utils.email_provider.send_mail_smtp_two_go", return_value=True) as smtp2go,
        patch("src.utils.email_provider.send_mail_gmail") as gmail,
    ):
        result = await send_email_provider(
            subject="Test",
            to=to,
            html="<p>hi</p>",
            logger=logger,
        )

    assert result == {"provider": "smtp2go"}
    smtp2go.assert_called_once()
    gmail.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_provider_falls_back_when_first_provider_fails(logger):
    to = [EmailInfo(email="user@example.com", name="User")]

    with (
        patch("src.utils.email_provider.inline_css", return_value="<p>hi</p>"),
        patch("src.utils.email_provider.render_text_from_html", return_value="hi"),
        patch(
            "src.utils.email_provider.send_mail_smtp_two_go",
            side_effect=RuntimeError("smtp down"),
        ),
        patch("src.utils.email_provider.send_mail_gmail", return_value=True) as gmail,
        patch("src.utils.email_provider.send_mail_elastic") as elastic,
    ):
        result = await send_email_provider(
            subject="Test",
            to=to,
            html="<p>hi</p>",
            logger=logger,
        )

    assert result == {"provider": "gmail"}
    gmail.assert_called_once()
    elastic.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_provider_raises_when_all_providers_fail(logger):
    to = [EmailInfo(email="user@example.com", name="User")]

    with (
        patch("src.utils.email_provider.inline_css", return_value="<p>hi</p>"),
        patch("src.utils.email_provider.render_text_from_html", return_value="hi"),
        patch(
            "src.utils.email_provider.send_mail_smtp_two_go",
            side_effect=RuntimeError("fail"),
        ),
        patch(
            "src.utils.email_provider.send_mail_gmail",
            side_effect=RuntimeError("fail"),
        ),
        patch(
            "src.utils.email_provider.send_mail_elastic",
            side_effect=RuntimeError("fail"),
        ),
        patch(
            "src.utils.email_provider.send_mail_mailersend",
            side_effect=RuntimeError("fail"),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await send_email_provider(
                subject="Test",
                to=to,
                html="<p>hi</p>",
                logger=logger,
            )

    assert exc_info.value.status_code == 500
