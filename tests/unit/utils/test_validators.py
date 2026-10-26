import pytest
from pydantic import ValidationError

from src.dto.sendOtp import SendOtpRequest
from src.utils.validators import validate_name

pytestmark = pytest.mark.unit


def test_validate_name_accepts_unicode_letters():
    assert validate_name("John Doe") == "John Doe"
    assert validate_name("  José  ") == "José"


def test_validate_name_rejects_digits():
    with pytest.raises(ValueError, match="letters"):
        validate_name("John 2")


def test_send_otp_request_requires_valid_email():
    with pytest.raises(ValidationError):
        SendOtpRequest(otp=123456, recipient="not-an-email", expiry_minutes=10)


def test_send_otp_request_accepts_valid_payload():
    data = SendOtpRequest(otp=123456, recipient="user@example.com", expiry_minutes=10)
    assert data.otp == 123456
    assert data.recipient == "user@example.com"
    assert data.expiry_minutes == 10
