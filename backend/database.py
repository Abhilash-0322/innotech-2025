from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = None
db = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    print(f"✅ Connected to MongoDB: {settings.database_name}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("🔒 MongoDB connection closed")


def get_database():
    """Get database instance"""
    return db
