import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_conn = None

def get_connection():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        _conn.autocommit = True
    return _conn

async def create_pool():
    get_connection()
    await create_tables()

async def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            referred_by BIGINT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS channels (
            id SERIAL PRIMARY KEY,
            channel_id TEXT NOT NULL,
            channel_link TEXT NOT NULL,
            channel_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS referral_projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            post_text TEXT,
            post_photo TEXT,
            channel_id TEXT,
            channel_link TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            auto_link_enabled BOOLEAN DEFAULT FALSE,
            auto_link_threshold INTEGER,
            auto_link_url TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            ended_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS referral_stats (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES referral_projects(id),
            user_id BIGINT REFERENCES users(id),
            referral_count INTEGER DEFAULT 0,
            UNIQUE(project_id, user_id)
        );
    """)
    cur.close()

async def get_pool():
    return get_connection()
