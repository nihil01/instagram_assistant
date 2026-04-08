import httpx


async def send_message(
    instagram_account_id: str,
    access_token: str,
    recipient_id: str,
    text: str,
):
    url = f"https://graph.instagram.com/v25.0/{instagram_account_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    body = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=body)

    return r.json()