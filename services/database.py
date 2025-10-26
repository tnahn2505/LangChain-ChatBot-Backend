"""
Database service for MongoDB connection
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = None
db = None

async def get_database():
    """Get database instance"""
    global client, db
    
    if client is None:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise Exception("MONGODB_URI not found in environment variables")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_uri)
        db_name = os.getenv("MONGODB_DB_NAME", "chatbotdb")
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {db_name}")
    
    return db

async def close_database():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")
