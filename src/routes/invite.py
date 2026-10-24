from fastapi import APIRouter, Depends, status

from src.config.config import get_request_logger
from src.dto.base import SuccessResponse
from src.dto.invite import BatchInviteRequest, BatchInviteResponse
from src.utils.services.invite_mail import send_invite_batch

router = APIRouter(tags=["invite"])


@router.post(
    "/batch",
    response_model=SuccessResponse[BatchInviteResponse],
    status_code=status.HTTP_200_OK,
)
async def send_invite_batch_route(
        data: BatchInviteRequest,
        logger=Depends(get_request_logger),
):
    result = await send_invite_batch(data, logger)
    return SuccessResponse[BatchInviteResponse](
        message="Invite batch processed",
        data=result,
    )
