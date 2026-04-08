import logging

from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_runtime import (
    fetch_recent_chat_history,
    get_company_runtime,
    persist_message,
)
from services.instagram_messaging import send_message
from services.openai_messaging import generate_reply

logger = logging.getLogger(__name__)


async def handle_message(event: dict, session: AsyncSession) -> None:
    sender_id = event["sender"]["id"]
    recipient_id = event["recipient"]["id"]
    message = event.get("message", {})
    text_message = message.get("text")
    mid = message.get("mid")

    if not text_message:
        logger.info("Skipping non-text message mid=%s", mid)
        return

    if sender_id == recipient_id:
        logger.warning("Blocked self-loop message sender=%s", sender_id)
        return

    company = await get_company_runtime(session, recipient_id)
    if not company:
        logger.warning("Unknown company for recipient instagram id=%s", recipient_id)
        return

    await persist_message(
        session,
        company_id=str(company["id"]),
        customer_id=sender_id,
        company_account_id=recipient_id,
        direction="inbound",
        text_message=text_message,
        instagram_mid=mid,
        payload=event,
    )

    history = await fetch_recent_chat_history(
        session,
        company_id=str(company["id"]),
        customer_id=sender_id,
    )

    reply = generate_reply(
        system_prompt=company["prompt_text"],
        user_text=text_message,
        history=history,
    )

    send_result = await send_message(
        instagram_account_id=recipient_id,
        access_token=company["access_token"],
        recipient_id=sender_id,
        text=reply,
    )

    await persist_message(
        session,
        company_id=str(company["id"]),
        customer_id=sender_id,
        company_account_id=recipient_id,
        direction="outbound",
        text_message=reply,
        instagram_mid=send_result.get("message_id"),
        payload=send_result,
    )

    logger.info("Handled message mid=%s for company=%s", mid, company["instagram_account_id"])
