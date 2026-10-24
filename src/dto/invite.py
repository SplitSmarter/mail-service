from enum import Enum
from typing import List, Literal, Optional

from pydantic import EmailStr, Field, HttpUrl

from src.utils.strict_base_model import StrictBaseModel
from src.utils.validators import NameField


class InviteTargetType(str, Enum):
    GROUP = "group"
    BUDGET = "budget"
    MEMORY = "memory"


class InviteSendStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"


class InviteRecipient(StrictBaseModel):
    invite_id: str = Field(min_length=1, max_length=64)
    recipient: EmailStr
    recipient_name: NameField
    link: HttpUrl


class BatchInviteRequest(StrictBaseModel):
    inviter_name: NameField
    target_type: InviteTargetType
    target_name: str = Field(min_length=1, max_length=120)
    lang: Literal["en"] = "en"
    recipients: List[InviteRecipient] = Field(min_length=1, max_length=25)


class InviteSendResult(StrictBaseModel):
    invite_id: str
    recipient: EmailStr
    status: InviteSendStatus
    provider: Optional[str] = None
    error: Optional[str] = None


class BatchInviteResponse(StrictBaseModel):
    results: List[InviteSendResult]
    sent_count: int
    failed_count: int
