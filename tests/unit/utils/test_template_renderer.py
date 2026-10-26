import pytest

from src.utils.template_renderer import render_template

pytestmark = pytest.mark.unit


def test_render_otp_template_includes_code_and_expiry():
    html = render_template(
        "send_otp.html",
        {"otp": 654321, "otp_expiry": 15},
        lang="en",
    )
    assert "654321" in html
    assert "15" in html


def test_render_reset_password_template_includes_link():
    link = "https://app.example.com/reset?token=abc"
    html = render_template(
        "reset_password.html",
        {"reset_link": link},
        lang="en",
    )
    assert link in html


def test_render_missing_template_raises():
    with pytest.raises(Exception):
        render_template("does_not_exist.html", {}, lang="en")
