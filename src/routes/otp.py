from fastapi import APIRouter, Depends, HTTPException, status

from src.config.config import get_request_logger
from src.dto.base import SuccessResponse
from src.dto.sendOtp import SendOtpRequest
from src.schemas.error_codes import get_error_http_exception, ErrorCode
from src.utils.services.otp_mail import send_otp_email

router = APIRouter(tags=["otp"])


@router.post(
    "/signup",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
)
async def send_signup_otp(
        data: SendOtpRequest,
        logger=Depends(get_request_logger)
):
    try:
        # TODO: Make this multilingual
        await send_otp_email(
            otp=data.otp,
            recipient=data.recipient,
            expiry_minutes=data.expiry_minutes,
            logger=logger
        )
        return SuccessResponse[None](
            message="OTP sent",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("An error occurred while sending OTP")
        raise get_error_http_exception(ErrorCode.INTERNAL_SERVER)
