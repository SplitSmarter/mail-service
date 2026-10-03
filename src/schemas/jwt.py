from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from src.utils.strict_base_model import StrictBaseModel


class JWTPayload(StrictBaseModel):
    sub: str  # Subject: usually user ID or unique identifier
    email: Optional[EmailStr]  # Optional email of the user
    roles: Optional[List[str]] = []  # Roles or permissions
    iat: Optional[int] = None  # Issued at timestamp (epoch)
    exp: Optional[int] = None  # Expiration timestamp (epoch)
    iss: Optional[str] = None  # Issuer
    aud: Optional[str] = None  # Audience (optional)

    def set_expiration(self, minutes: int = 60):
        """Set expiration time from now in minutes"""
        now = datetime.now(timezone.utc)
        self.iat = int(now.timestamp())
        self.exp = int((now + timedelta(minutes=minutes)).timestamp())
