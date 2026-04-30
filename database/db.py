import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None

async def create_pool():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL)
    await create_tables()

async def create_tables():
    async with _pool.acquire() as conn:
        await conn.execute("""
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

async def get_pool():
    return _pool
