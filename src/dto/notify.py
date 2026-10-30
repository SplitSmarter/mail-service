from typing import Literal, Optional

from pydantic import Field

from src.utils.strict_base_model import StrictBaseModel


class NotifyMailRequest(StrictBaseModel):
    contact: str = Field(min_length=1, max_length=254)


class NotifyMailResponse(StrictBaseModel):
    provider: Optional[str] = None
    kind: Literal["email", "phone"]
