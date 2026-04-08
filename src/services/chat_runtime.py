import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


MAX_HISTORY_MESSAGES = 10
MAX_PROMPT_LENGTH = 3000


async def get_company_runtime(session: AsyncSession, instagram_account_id: str) -> dict[str, Any] | None:
    query = text(
        """
        select
            c.id,
            c.instagram_account_id,
            c.username,
            t.access_token,
            coalesce(p.prompt_text, :default_prompt) as prompt_text
        from instagram_companies c
        join instagram_tokens t on t.company_id = c.id and t.is_active = true
        left join instagram_system_prompts p on p.company_id = c.id and p.is_active = true
        where c.instagram_account_id = :id
        """
    )

    result = await session.execute(
        query,
        {
            "id": instagram_account_id,
            "default_prompt": "Ты AI-ассистент компании в Instagram Direct. Отвечай коротко, дружелюбно и по делу.",
        },
    )
    company = result.mappings().first()
    if not company:
        logger.warning("Company runtime not found for instagram_account_id=%s", instagram_account_id)
    return company


async def get_company_by_username(session: AsyncSession, username: str) -> dict[str, Any] | None:
    result = await session.execute(
        text(
            """
            select id, instagram_account_id, username
            from instagram_companies
            where lower(username) = lower(:username)
            limit 1
            """
        ),
        {"username": username.strip()},
    )
    return result.mappings().first()


async def set_active_prompt_by_username(
    session: AsyncSession,
    username: str,
    prompt_text: str,
    title: str = "Client prompt",
) -> bool:
    company = await get_company_by_username(session, username)
    if not company:
        return False

    now = datetime.now(timezone.utc)

    await session.execute(
        text(
            """
            update instagram_system_prompts
            set is_active = false,
                updated_at = :now
            where company_id = :company_id and is_active = true
            """
        ),
        {"company_id": company["id"], "now": now},
    )

    await session.execute(
        text(
            """
            insert into instagram_system_prompts (
                company_id,
                title,
                prompt_text,
                is_active,
                version,
                created_at,
                updated_at
            )
            values (
                :company_id,
                :title,
                :prompt_text,
                true,
                coalesce((
                    select max(version) + 1
                    from instagram_system_prompts
                    where company_id = :company_id
                ), 1),
                :now,
                :now
            )
            """
        ),
        {
            "company_id": company["id"],
            "title": title,
            "prompt_text": prompt_text,
            "now": now,
        },
    )

    await session.commit()
    logger.info("Updated active system prompt for username=%s", username)
    return True


async def persist_message(
    session: AsyncSession,
    *,
    company_id: str,
    customer_id: str,
    company_account_id: str,
    direction: str,
    text_message: str,
    instagram_mid: str | None,
    payload: dict[str, Any],
) -> None:
    now = datetime.now(timezone.utc)

    await session.execute(
        text(
            """
            insert into instagram_conversations (
                company_id,
                customer_instagram_id,
                last_message_at,
                created_at,
                updated_at
            )
            values (:company_id, :customer_id, :now, :now, :now)
            on conflict (company_id, customer_instagram_id)
            do update set
                last_message_at = excluded.last_message_at,
                updated_at = excluded.updated_at
            """
        ),
        {
            "company_id": company_id,
            "customer_id": customer_id,
            "now": now,
        },
    )

    conversation_result = await session.execute(
        text(
            """
            select id from instagram_conversations
            where company_id = :company_id and customer_instagram_id = :customer_id
            limit 1
            """
        ),
        {"company_id": company_id, "customer_id": customer_id},
    )
    conversation_id = conversation_result.scalar_one()

    sender_id = customer_id if direction == "inbound" else company_account_id
    recipient_id = company_account_id if direction == "inbound" else customer_id

    await session.execute(
        text(
            """
            insert into instagram_messages (
                conversation_id,
                company_id,
                instagram_mid,
                sender_instagram_id,
                recipient_instagram_id,
                direction,
                message_text,
                message_payload,
                sent_at,
                created_at
            )
            values (
                :conversation_id,
                :company_id,
                :instagram_mid,
                :sender_id,
                :recipient_id,
                :direction,
                :message_text,
                cast(:message_payload as jsonb),
                :now,
                :now
            )
            on conflict (company_id, instagram_mid) do nothing
            """
        ),
        {
            "conversation_id": conversation_id,
            "company_id": company_id,
            "instagram_mid": instagram_mid,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "direction": direction,
            "message_text": text_message,
            "message_payload": json.dumps(payload),
            "now": now,
        },
    )

    await session.commit()


async def fetch_recent_chat_history(
    session: AsyncSession,
    *,
    company_id: str,
    customer_id: str,
    limit: int = MAX_HISTORY_MESSAGES,
) -> list[dict[str, str]]:
    result = await session.execute(
        text(
            """
            select direction, message_text
            from instagram_messages m
            join instagram_conversations c on c.id = m.conversation_id
            where m.company_id = :company_id
              and c.customer_instagram_id = :customer_id
              and m.message_text is not null
            order by m.created_at desc
            limit :limit
            """
        ),
        {"company_id": company_id, "customer_id": customer_id, "limit": limit},
    )

    history = []
    for row in reversed(result.mappings().all()):
        role = "user" if row["direction"] == "inbound" else "assistant"
        history.append({"role": role, "content": row["message_text"]})

    return history
