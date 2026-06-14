from pydantic import EmailStr

from src.utils.strict_base_model import StrictBaseModel


class EmailInfo(StrictBaseModel):
    email: EmailStr
    name: str

class MailResponse(StrictBaseModel):
    email: EmailStr