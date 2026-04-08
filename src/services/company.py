from sqlalchemy import text

async def upsert_company(db, instagram_account_id, username, name, token, expires_in):

    await db.execute(text("""
    insert into instagram_companies (instagram_account_id, username, display_name)
    values (:id, :u, :n)
    on conflict (instagram_account_id)
    do update set username = :u, display_name = :n
    """), {"id": instagram_account_id, "u": username, "n": name})

    await db.execute(text("""
    update instagram_tokens set is_active=false where company_id in (
        select id from instagram_companies where instagram_account_id=:id
    )
    """), {"id": instagram_account_id})

    await db.execute(text("""
    insert into instagram_tokens (
        company_id, access_token, issued_at, expires_at, refresh_after, is_active
    )
    select 
        id,
        :token,
        now(),
        now() + (:expires_in || ' seconds')::interval,
        now() + ((:expires_in - 86400) || ' seconds')::interval,
        true
    from instagram_companies where instagram_account_id=:id
    """), {
        "id": instagram_account_id,
        "token": token,
        "expires_in": expires_in
    })

    await db.commit()