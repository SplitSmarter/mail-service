from pydantic import EmailStr

from src.utils.strict_base_model import StrictBaseModel
from src.utils.validators import NameField

class SendOtpRequest(StrictBaseModel):
    otp: int
    recipient: EmailStr
    expiry_minutes: int

class ResetPasswordRequest(StrictBaseModel):
    reset_link: str
    recipient: EmailStr
