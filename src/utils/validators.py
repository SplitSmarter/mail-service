from typing import Annotated
import regex
from pydantic import Field, AfterValidator

def validate_name(v: str) -> str:
    v = v.strip()
    if not regex.fullmatch(r"^\p{L}[\p{L} \p{M}'\-·]*\p{L}$", v):
        raise ValueError("Name must contain only letters and valid punctuation")
    return v

NameField = Annotated[
    str,
    AfterValidator(validate_name),
    Field(
        examples=["John Doe"],
        description="Full name (Unicode letters, 1-100 chars)"
    )
]