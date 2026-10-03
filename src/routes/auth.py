from fastapi import APIRouter, Depends, HTTPException, status

from src.config.config import get_request_logger
from src.dto.base import SuccessResponse
from src.dto.sendOtp import ResetPasswordRequest
from src.schemas.error_codes import get_error_http_exception, ErrorCode
from src.utils.services.reset_password import send_reset_password_email

router = APIRouter(tags=["auth"], prefix="/v1")


@router.post(
    "/reset-password",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
)
async def send_reset_password(
        data: ResetPasswordRequest,
        logger=Depends(get_request_logger)
):
    try:
        # TODO: Make this multilingual
        await send_reset_password_email(
            reset_link=data.reset_link,
            recipient=data.recipient,
            logger=logger
        )
        return SuccessResponse[None](
            message="reset password mail sent",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("An error occurred while sending reset password email")
        raise get_error_http_exception(ErrorCode.INTERNAL_SERVER)
