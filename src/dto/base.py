# src/dto/base.py
from typing import Generic, TypeVar, Optional
from src.dto.pagination import PaginationResponse
from src.utils.strict_base_model import StrictBaseModel

T = TypeVar("T")
M = TypeVar("M")


class SuccessResponse(StrictBaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    pagination: Optional[PaginationResponse] = None


class ErrorResponse(StrictBaseModel, Generic[T, M]):
    success: bool = False
    message: Optional[str] = None
    error: Optional[T] = None
    meta: Optional[M] = None
