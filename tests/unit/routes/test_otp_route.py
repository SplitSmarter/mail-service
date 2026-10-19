from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.unit


def test_signup_otp_success(client):
    with patch(
        "src.routes.otp.send_otp_email",
        new_callable=AsyncMock,
        return_value={"provider": "gmail"},
    ) as send_otp:
        response = client.post(
            "/otp/signup",
            json={
                "otp": 123456,
                "recipient": "user@example.com",
                "expiry_minutes": 10,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "OTP sent"
    send_otp.assert_awaited_once()


def test_signup_otp_validation_error(client):
    response = client.post(
        "/otp/signup",
        json={
            "otp": 123456,
            "recipient": "not-an-email",
            "expiry_minutes": 10,
        },
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
