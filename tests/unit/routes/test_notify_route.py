from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.unit


def test_notify_mail_accepts_only_the_contact(client):
    with patch(
        "src.routes.notify.send_notify_mail",
        new_callable=AsyncMock,
        return_value={"provider": "smtp2go", "kind": "email"},
    ) as send_notify:
        response = client.post("/notify", json={"contact": "ada@example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["kind"] == "email"
    send_notify.assert_awaited_once()
    assert send_notify.await_args.args[0] == "ada@example.com"


def test_notify_mail_rejects_a_chosen_recipient(client):
    response = client.post(
        "/notify",
        json={"contact": "ada@example.com", "to": "other@example.com"},
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
