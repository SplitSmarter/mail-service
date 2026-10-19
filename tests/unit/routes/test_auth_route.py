from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.unit


def test_reset_password_success(client):
    with patch(
        "src.routes.auth.send_reset_password_email",
        new_callable=AsyncMock,
        return_value={"provider": "gmail"},
    ) as send_reset:
        response = client.post(
            "/auth/v1/reset-password",
            json={
                "reset_link": "https://app.example.com/reset?token=abc",
                "recipient": "user@example.com",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "reset password mail sent"
    send_reset.assert_awaited_once()


def test_reset_password_validation_error(client):
    response = client.post(
        "/auth/v1/reset-password",
        json={
            "reset_link": "https://app.example.com/reset?token=abc",
            "recipient": "bad-email",
        },
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
