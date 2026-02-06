import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "learning")

# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)

# Get database and collection
database = client[DATABASE_NAME]
user_collection = database.get_collection("users")
