from database.db import get_connection

def _exec(sql, params=(), fetch=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    if fetch == "one":
        result = cur.fetchone()
    elif fetch == "all":
        result = cur.fetchall()
    elif fetch == "val":
        row = cur.fetchone()
        result = list(row.values())[0] if row else None
    else:
        result = None
    cur.close()
    return result

# ─── USERS ───────────────────────────────────────────────
async def get_user(user_id):
    return _exec("SELECT * FROM users WHERE id=%s", (user_id,), fetch="one")

async def create_user(user_id, username, full_name, language, referred_by=None):
    _exec("""
        INSERT INTO users (id, username, full_name, language, referred_by)
        VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING
    """, (user_id, username, full_name, language, referred_by))

async def update_user_language(user_id, language):
    _exec("UPDATE users SET language=%s WHERE id=%s", (language, user_id))

async def get_total_users():
    return _exec("SELECT COUNT(*) as c FROM users", fetch="val")

async def get_today_users():
    return _exec("SELECT COUNT(*) as c FROM users WHERE created_at >= CURRENT_DATE", fetch="val")

async def get_all_user_ids():
    rows = _exec("SELECT id FROM users", fetch="all")
    return [r['id'] for r in rows] if rows else []

# ─── CHANNELS ────────────────────────────────────────────
async def add_channel(channel_id, channel_link, channel_name):
    _exec("INSERT INTO channels (channel_id, channel_link, channel_name) VALUES (%s,%s,%s)",
          (channel_id, channel_link, channel_name))

async def get_active_channels():
    return _exec("SELECT * FROM channels WHERE is_active=TRUE", fetch="all") or []

async def remove_channel(channel_id_db):
    _exec("UPDATE channels SET is_active=FALSE WHERE id=%s", (channel_id_db,))

# ─── REFERRAL PROJECTS ───────────────────────────────────
async def create_project(name, post_text, post_photo, channel_id, channel_link,
                          auto_link_enabled, auto_link_threshold, auto_link_url):
    _exec("UPDATE referral_projects SET is_active=FALSE")
    result = _exec("""
        INSERT INTO referral_projects
        (name, post_text, post_photo, channel_id, channel_link,
         is_active, auto_link_enabled, auto_link_threshold, auto_link_url)
        VALUES (%s,%s,%s,%s,%s,TRUE,%s,%s,%s) RETURNING id
    """, (name, post_text, post_photo, channel_id, channel_link,
          auto_link_enabled, auto_link_threshold, auto_link_url), fetch="one")
    return result['id'] if result else None

async def get_active_project():
    return _exec("SELECT * FROM referral_projects WHERE is_active=TRUE ORDER BY id DESC LIMIT 1", fetch="one")

async def end_project(project_id):
    _exec("UPDATE referral_projects SET is_active=FALSE, ended_at=NOW() WHERE id=%s", (project_id,))

# ─── REFERRAL STATS ──────────────────────────────────────
async def add_referral_stat(project_id, user_id):
    _exec("""
        INSERT INTO referral_stats (project_id, user_id, referral_count)
        VALUES (%s,%s,1)
        ON CONFLICT (project_id, user_id)
        DO UPDATE SET referral_count = referral_stats.referral_count + 1
    """, (project_id, user_id))

async def get_project_stats(project_id):
    return _exec("""
        SELECT u.full_name, u.username, rs.referral_count
        FROM referral_stats rs
        JOIN users u ON u.id = rs.user_id
        WHERE rs.project_id=%s
        ORDER BY rs.referral_count DESC
    """, (project_id,), fetch="all") or []

async def get_user_referral_count(project_id, user_id):
    result = _exec("""
        SELECT referral_count FROM referral_stats
        WHERE project_id=%s AND user_id=%s
    """, (project_id, user_id), fetch="val")
    return result or 0

async def get_total_referral_links():
    return _exec("SELECT COUNT(DISTINCT user_id) as c FROM referral_stats", fetch="val") or 0
