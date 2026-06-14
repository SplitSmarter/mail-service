from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.dto.sendOtp import SendOtpRequest
from src.utils.services.otp_mail import send_otp_email

router = APIRouter()

@router.post("/user/invite")
async def send_signup_otp(
        request: Request,
        data: SendOtpRequest,
):
    try:
        response = send_otp_email(otp=data.otp, recipient=data.recipient, name=data.name, expiry_minutes=data.expiry_minutes)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "otp": data.otp,
                "data": response,
                "message": "OTP sent successfully",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "server_error",
                "message": "An error occurred"
            }
        )