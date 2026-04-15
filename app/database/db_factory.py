"""
Database factory for switching between MongoDB and PostgreSQL.
Allows learning both database systems simultaneously.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()

if DB_TYPE == "mongodb":
    from app.database.mongodb_connection import users_collection, todos_collection
    DATABASE_BACKEND = "mongodb"
    
elif DB_TYPE == "postgresql":
    from app.database.connection import AsyncSessionLocal, get_db
    DATABASE_BACKEND = "postgresql"
else:
    raise ValueError(f"Invalid DB_TYPE: {DB_TYPE}. Must be 'mongodb' or 'postgresql'")

__all__ = ["DB_TYPE", "DATABASE_BACKEND"]
