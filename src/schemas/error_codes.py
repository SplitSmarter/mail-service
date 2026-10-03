import enum

from fastapi import HTTPException
from starlette import status

from src.dto.base import ErrorResponse

class ErrorCode(enum.Enum):
    INTERNAL_SERVER = "internal_server_error"
    VALIDATION_ERROR = "validation_error"
    ACCESS_DENIED = "access_denied"
    UNAUTHENTICATED = "unauthenticated"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"  # When a resource already exists
    BAD_REQUEST = "bad_request"  # Malformed request or invalid input
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"  # Too many requests
    SERVICE_UNAVAILABLE = "service_unavailable"  # External service or dependency failed
    TIMEOUT = "timeout"  # Request or process took too long
    DEPENDENCY_ERROR = "dependency_error"  # Related resource or service issue
    FORBIDDEN_ACTION = "forbidden_action"  # Valid request but not allowed logically
    RESOURCE_LOCKED = "resource_locked"  # Resource temporarily locked or in use
    DUPLICATE_ENTRY = "duplicate_entry"  # Unique constraint violation
    DATA_INTEGRITY_ERROR = "data_integrity_error"  # Inconsistent or broken data
    RESOURCE_DELETED = "resource_deleted"  # The resource has been deleted
    EXPIRED_RESOURCE = "expired_resource"  # Resource or token has expired
    UNSUPPORTED_OPERATION = "unsupported_operation"  # Operation not supported
    VERSION_CONFLICT = "version_conflict"  # Stale data update attempt
    INSUFFICIENT_STORAGE = "insufficient_storage"  # Not enough space to process request
    INVALID_STATE = "invalid_state"  # Resource is in a state that prevents the operation
    DEPENDENT_RESOURCE_EXISTS = "dependent_resource_exists"  # Can't delete or modify due to dependencies
    PRECONDITION_FAILED = "precondition_failed"  # Required conditions not met
    METHOD_NOT_ALLOWED = "method_not_allowed"  # HTTP method not supported
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"  # Invalid or unsupported content type


class ErrorCodeMessage(enum.Enum):
    INTERNAL_SERVER = "An internal server error occurred"
    VALIDATION_ERROR = "Validation error occurred"
    ACCESS_DENIED = "Insufficient permissions to access this resource"
    UNAUTHENTICATED = "You are not authenticated to access this resource"
    NOT_FOUND = "Resource not found"
    CONFLICT = "A similar resource already exists"
    BAD_REQUEST = "Invalid request data or parameters"
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later"
    SERVICE_UNAVAILABLE = "A required service is currently unavailable"
    TIMEOUT = "The request took too long to process"
    DEPENDENCY_ERROR = "An error occurred with a dependent service or resource"
    FORBIDDEN_ACTION = "This action is not permitted"
    RESOURCE_LOCKED = "The resource is temporarily locked or being updated"
    DUPLICATE_ENTRY = "Duplicate data found where unique value was expected"
    DATA_INTEGRITY_ERROR = "Data inconsistency detected. Please try again"
    RESOURCE_DELETED = "This resource has been deleted and is no longer available"
    EXPIRED_RESOURCE = "The requested resource or token has expired"
    UNSUPPORTED_OPERATION = "This operation is not supported"
    VERSION_CONFLICT = "The resource was modified by another process. Please refresh and try again"
    INSUFFICIENT_STORAGE = "Not enough storage available to complete this operation"
    INVALID_STATE = "The resource is in an invalid state for this operation"
    DEPENDENT_RESOURCE_EXISTS = "This resource cannot be modified or deleted because dependent resources exist"
    PRECONDITION_FAILED = "One or more required conditions were not met for this operation"
    METHOD_NOT_ALLOWED = "The requested HTTP method is not supported for this resource"
    UNSUPPORTED_MEDIA_TYPE = "The content type or format of the request is not supported"


class ErrorHTTPStatus(enum.Enum):
    INTERNAL_SERVER = status.HTTP_500_INTERNAL_SERVER_ERROR
    VALIDATION_ERROR = status.HTTP_422_UNPROCESSABLE_ENTITY
    ACCESS_DENIED = status.HTTP_403_FORBIDDEN
    UNAUTHENTICATED = status.HTTP_401_UNAUTHORIZED
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    CONFLICT = status.HTTP_409_CONFLICT
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    RATE_LIMIT_EXCEEDED = status.HTTP_429_TOO_MANY_REQUESTS
    SERVICE_UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE
    TIMEOUT = status.HTTP_504_GATEWAY_TIMEOUT
    DEPENDENCY_ERROR = status.HTTP_424_FAILED_DEPENDENCY
    FORBIDDEN_ACTION = status.HTTP_403_FORBIDDEN
    RESOURCE_LOCKED = status.HTTP_423_LOCKED
    DUPLICATE_ENTRY = status.HTTP_409_CONFLICT
    DATA_INTEGRITY_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    RESOURCE_DELETED = status.HTTP_410_GONE
    EXPIRED_RESOURCE = status.HTTP_410_GONE
    UNSUPPORTED_OPERATION = status.HTTP_501_NOT_IMPLEMENTED
    VERSION_CONFLICT = status.HTTP_409_CONFLICT
    INSUFFICIENT_STORAGE = status.HTTP_507_INSUFFICIENT_STORAGE
    INVALID_STATE = status.HTTP_400_BAD_REQUEST
    DEPENDENT_RESOURCE_EXISTS = status.HTTP_409_CONFLICT
    PRECONDITION_FAILED = status.HTTP_412_PRECONDITION_FAILED
    METHOD_NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
    UNSUPPORTED_MEDIA_TYPE = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def get_error_http_exception(code: ErrorCode) -> HTTPException:
    """Return a standardized FastAPI HTTPException for the given error code."""
    return HTTPException(
        status_code=ErrorHTTPStatus[code.name].value,
        detail=ErrorResponse[str, None](
            error=code.value,
            message=ErrorCodeMessage[code.name].value
        ).model_dump()
    )


class ErrorReason(enum.Enum):
    user_exists: "user_exists"
    mail_not_sent: "mail_not_sent"
