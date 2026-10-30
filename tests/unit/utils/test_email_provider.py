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


def _quiet_render():
    return (
        patch("src.utils.email_provider.inline_css", return_value="<p>hi</p>"),
        patch("src.utils.email_provider.render_text_from_html", return_value="hi"),
    )


@pytest.mark.asyncio
async def test_send_email_provider_uses_brevo_and_skips_disabled_providers(logger):
    to = [EmailInfo(email="user@example.com", name="User")]
    render = _quiet_render()

    with (
        render[0],
        render[1],
        patch("src.utils.email_provider.send_mail_brevo", return_value=True) as brevo,
        patch("src.utils.email_provider.send_mail_smtp_two_go") as smtp2go,
    ):
        result = await send_email_provider(
            subject="Test",
            to=to,
            html="<p>hi</p>",
            logger=logger,
        )

    assert result == {"provider": "brevo"}
    brevo.assert_called_once()
    smtp2go.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_provider_uses_gmail_when_its_flag_is_on(logger):
    to = [EmailInfo(email="user@example.com", name="User")]
    render = _quiet_render()

    with (
        render[0],
        render[1],
        patch("src.utils.email_provider.GMAIL_ENABLED", True),
        patch("src.utils.email_provider.send_mail_brevo", return_value=False),
        patch("src.utils.email_provider.send_mail_smtp_two_go") as smtp2go,
        patch("src.utils.email_provider.send_mail_gmail", return_value=True) as gmail,
    ):
        result = await send_email_provider(
            subject="Test",
            to=to,
            html="<p>hi</p>",
            logger=logger,
        )

    assert result == {"provider": "gmail"}
    gmail.assert_called_once()
    smtp2go.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_provider_skips_gmail_when_its_flag_is_off(logger):
    to = [EmailInfo(email="user@example.com", name="User")]
    render = _quiet_render()

    with (
        render[0],
        render[1],
        patch("src.utils.email_provider.GMAIL_ENABLED", False),
        patch("src.utils.email_provider.send_mail_brevo", return_value=False),
        patch("src.utils.email_provider.send_mail_gmail") as gmail,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await send_email_provider(
                subject="Test",
                to=to,
                html="<p>hi</p>",
                logger=logger,
            )

    assert exc_info.value.status_code == 500
    gmail.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_provider_raises_when_enabled_providers_fail(logger):
    to = [EmailInfo(email="user@example.com", name="User")]
    render = _quiet_render()

    with (
        render[0],
        render[1],
        patch("src.utils.email_provider.send_mail_brevo", side_effect=RuntimeError("fail")),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await send_email_provider(
                subject="Test",
                to=to,
                html="<p>hi</p>",
                logger=logger,
            )

    assert exc_info.value.status_code == 500
