from services.openai_messaging import generate_reply
from services.instagram_messaging import send_message
from services.company_runtime import get_company_runtime


async def handle_message(event, session):
    sender_id = event["sender"]["id"]
    recipient_id = event["recipient"]["id"]
    text = event["message"].get("text")
    # mid = event["message"].get("mid")

    if not text:
        return

    # 🔥 защита от self-loop
    if sender_id == recipient_id:
        return

    company = await get_company_runtime(session, recipient_id)

    if not company:
        return

    reply = generate_reply(company["prompt_text"], text)

    await send_message(
        instagram_account_id=recipient_id,
        access_token=company["access_token"],
        recipient_id=sender_id,
        text=reply
    )
