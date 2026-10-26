import logging

from fastapi import HTTPException

from src.dto.invite import (
    BatchInviteRequest,
    BatchInviteResponse,
    InviteSendResult,
    InviteSendStatus,
)
from src.schemas.email_info import EmailInfo
from src.utils.email_provider import send_email_provider
from src.utils.template_renderer import render_template


async def send_invite_batch(
        data: BatchInviteRequest,
        logger: logging.Logger,
) -> BatchInviteResponse:
    results: list[InviteSendResult] = []
    for item in data.recipients:
        try:
            html = render_template(
                "invite.html",
                {
                    "inviter_name": data.inviter_name,
                    "recipient_name": item.recipient_name,
                    "target_type": data.target_type.value,
                    "target_name": data.target_name.strip(),
                    "link": str(item.link),
                },
                data.lang,
            )
            response = await send_email_provider(
                subject=f"Invitation to {data.target_name.strip()}",
                to=[EmailInfo(email=item.recipient, name=item.recipient_name)],
                html=html,
                logger=logger,
            )
            results.append(
                InviteSendResult(
                    invite_id=item.invite_id,
                    recipient=item.recipient,
                    status=InviteSendStatus.SENT,
                    provider=response.get("provider"),
                )
            )
        except HTTPException as exc:
            detail = exc.detail
            message = detail.get("message") if isinstance(detail, dict) else str(detail)
            logger.warning("Invite email failed for %s: %s", item.recipient, message)
            results.append(
                InviteSendResult(
                    invite_id=item.invite_id,
                    recipient=item.recipient,
                    status=InviteSendStatus.FAILED,
                    error=message or "mail_not_sent",
                )
            )
        except Exception:
            logger.exception("Invite email failed for %s", item.recipient)
            results.append(
                InviteSendResult(
                    invite_id=item.invite_id,
                    recipient=item.recipient,
                    status=InviteSendStatus.FAILED,
                    error="mail_not_sent",
                )
            )

    sent_count = sum(1 for result in results if result.status == InviteSendStatus.SENT)
    return BatchInviteResponse(
        results=results,
        sent_count=sent_count,
        failed_count=len(results) - sent_count,
    )
