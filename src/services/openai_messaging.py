import logging
from typing import Sequence

from openai import OpenAI

from config.app_config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_reply(system_prompt: str, user_text: str, history: Sequence[dict[str, str]] | None = None) -> str:
    try:
        if not system_prompt:
            logger.warning("System prompt is empty; fallback message returned")
            return "Please, contact the account owner, I can not proceed your request now"

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )

        ai_text = (response.choices[0].message.content or "").strip()
        if not ai_text:
            logger.warning("Empty AI response received")
            return "Sorry, I can not proceed your request now 🙏"

        return ai_text

    except Exception:
        logger.exception("AI generate_reply failed")
        return "Sorry, I can not proceed your request now 🙏"
