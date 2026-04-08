from sqlalchemy import text


async def get_company_runtime(session, instagram_account_id: str):
    query = text("""
    select
        c.id,
        c.instagram_account_id,
        t.access_token,
        p.prompt_text
    from instagram_companies c
    join instagram_tokens t on t.company_id = c.id and t.is_active = true
    left join instagram_system_prompts p on p.company_id = c.id and p.is_active = true
    where c.instagram_account_id = :id
    """)

    result = await session.execute(query, {"id": instagram_account_id})
    return result.mappings().first()