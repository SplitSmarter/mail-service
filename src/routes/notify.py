from fastapi import APIRouter, Depends, HTTPException, status

from src.config.config import get_request_logger
from src.dto.base import SuccessResponse
from src.dto.notify import NotifyMailRequest, NotifyMailResponse
from src.schemas.error_codes import ErrorCode, get_error_http_exception
from src.utils.services.notify_mail import send_notify_mail

router = APIRouter(tags=["notify"])


@router.post(
    "",
    response_model=SuccessResponse[NotifyMailResponse],
    status_code=status.HTTP_200_OK,
)
async def send_notify(
        data: NotifyMailRequest,
        logger=Depends(get_request_logger),
):
    try:
        result = await send_notify_mail(data.contact, logger)
        return SuccessResponse[NotifyMailResponse](
            message="Notify mail sent",
            data=NotifyMailResponse.model_validate(result),
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("An error occurred while sending notify mail")
        raise get_error_http_exception(ErrorCode.INTERNAL_SERVER)
