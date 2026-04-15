"""
Database initialization script.
Creates all tables in PostgreSQL.

Run this once to set up the database:
    python init_db.py
"""

import asyncio
from app.database.connection import engine, Base
from app.database.models import User, Todo

async def init_db():
    """Create all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
