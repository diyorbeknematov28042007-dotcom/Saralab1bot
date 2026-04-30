from database.db import get_pool

# ─── USERS ───────────────────────────────────────────────
async def get_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)

async def create_user(user_id: int, username: str, full_name: str, language: str, referred_by: int = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (id, username, full_name, language, referred_by)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO NOTHING
        """, user_id, username, full_name, language, referred_by)

async def update_user_language(user_id: int, language: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET language=$1 WHERE id=$2", language, user_id)

async def get_total_users():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")

async def get_today_users():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE"
        )

# ─── CHANNELS ────────────────────────────────────────────
async def add_channel(channel_id: str, channel_link: str, channel_name: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO channels (channel_id, channel_link, channel_name)
            VALUES ($1, $2, $3)
        """, channel_id, channel_link, channel_name)

async def get_active_channels():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM channels WHERE is_active=TRUE")

async def remove_channel(channel_id_db: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE channels SET is_active=FALSE WHERE id=$1", channel_id_db)

# ─── REFERRAL PROJECTS ───────────────────────────────────
async def create_project(name, post_text, post_photo, channel_id, channel_link,
                          auto_link_enabled, auto_link_threshold, auto_link_url):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO referral_projects
            (name, post_text, post_photo, channel_id, channel_link,
             auto_link_enabled, auto_link_threshold, auto_link_url)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            RETURNING id
        """, name, post_text, post_photo, channel_id, channel_link,
            auto_link_enabled, auto_link_threshold, auto_link_url)

async def get_active_project():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM referral_projects WHERE is_active=TRUE ORDER BY id DESC LIMIT 1"
        )

async def end_project(project_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE referral_projects SET is_active=FALSE, ended_at=NOW()
            WHERE id=$1
        """, project_id)

async def get_all_projects():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM referral_projects ORDER BY id DESC")

# ─── REFERRAL STATS ──────────────────────────────────────
async def add_referral_stat(project_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO referral_stats (project_id, user_id, referral_count)
            VALUES ($1, $2, 1)
            ON CONFLICT (project_id, user_id)
            DO UPDATE SET referral_count = referral_stats.referral_count + 1
        """, project_id, user_id)

async def get_project_stats(project_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT u.full_name, u.username, rs.referral_count
            FROM referral_stats rs
            JOIN users u ON u.id = rs.user_id
            WHERE rs.project_id=$1
            ORDER BY rs.referral_count DESC
        """, project_id)

async def get_user_referral_count(project_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT referral_count FROM referral_stats
            WHERE project_id=$1 AND user_id=$2
        """, project_id, user_id) or 0

async def get_total_referral_links():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(DISTINCT user_id) FROM referral_stats")
