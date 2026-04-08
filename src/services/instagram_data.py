from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    InstagramCompany,
    InstagramToken,
    InstagramConversation,
    InstagramMessage,
    InstagramWebhookEvent,
    InstagramSystemPrompt,
    InstagramDataDeletionRequest,
)


async def _find_company_by_meta_user_id(
    db: AsyncSession,
    user_id: str,
) -> InstagramCompany | None:
    if not user_id:
        return None

    result = await db.execute(
        select(InstagramCompany).where(
            (InstagramCompany.instagram_account_id == user_id)
            | (InstagramCompany.app_scoped_user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def handle_deauthorize(
    db: AsyncSession,
    user_id: str,
    payload: dict,
) -> None:
    company = await _find_company_by_meta_user_id(db, user_id)
    if not company:
        await db.commit()
        return

    now = datetime.now(timezone.utc)

    company.status = "deauthorized"
    company.deauthorized_at = now
    company.updated_at = now

    await db.execute(
        update(InstagramToken)
        .where(InstagramToken.company_id == company.id)
        .values(
            is_active=False,
            updated_at=now,
        )
    )

    await db.commit()


async def handle_delete_data(
    db: AsyncSession,
    user_id: str,
    confirmation_code: UUID,
    payload: dict,
) -> None:
    company = await _find_company_by_meta_user_id(db, user_id)

    deletion_request = InstagramDataDeletionRequest(
        confirmation_code=confirmation_code,
        company_id=company.id if company else None,
        request_payload=payload,
        status="completed",
    )
    db.add(deletion_request)

    if not company:
        await db.commit()
        return

    now = datetime.now(timezone.utc)

    await db.execute(
        delete(InstagramMessage).where(
            InstagramMessage.company_id == company.id
        )
    )

    await db.execute(
        delete(InstagramWebhookEvent).where(
            InstagramWebhookEvent.company_id == company.id
        )
    )

    await db.execute(
        delete(InstagramConversation).where(
            InstagramConversation.company_id == company.id
        )
    )

    await db.execute(
        delete(InstagramSystemPrompt).where(
            InstagramSystemPrompt.company_id == company.id
        )
    )

    await db.execute(
        delete(InstagramToken).where(
            InstagramToken.company_id == company.id
        )
    )

    company.status = "deleted"
    company.deleted_at = now
    company.updated_at = now

    await db.commit()