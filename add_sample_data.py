"""
Add sample data to MongoDB for testing
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def add_sample_data():
    """Add sample thread and messages to MongoDB"""
    print("Adding sample data to MongoDB...")
    
    load_dotenv()
    
    # Get MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://langchain123:langchain12345@cluster0.xkcslrj.mongodb.net/?appName=Cluster0")
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not found")
        return
    
    db_name = os.getenv("MONGODB_DB_NAME", "chatbotdb")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_uri)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print(f"SUCCESS: Connected to MongoDB: {db_name}")
        
        # Create sample thread
        thread_id = "thread_sample_20251026_001"
        thread_doc = {
            "id": thread_id,
            "title": "Sample Chat",
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
        
        # Insert thread
        await db.threads.insert_one(thread_doc)
        print(f"SUCCESS: Added thread: {thread_id}")
        
        # Create sample messages
        messages = [
            {
                "id": f"msg_{thread_id}_user_001",
                "threadId": thread_id,
                "role": "user",
                "content": "Xin chao! Ban co the giup toi khong?",
                "createdAt": datetime.utcnow().isoformat()
            },
            {
                "id": f"msg_{thread_id}_assistant_001",
                "threadId": thread_id,
                "role": "assistant",
                "content": "Xin chao! Toi la AI Assistant. Toi co the giup ban tra loi cac cau hoi va ho tro ban trong nhieu linh vuc. Ban can ho tro gi?",
                "createdAt": datetime.utcnow().isoformat()
            },
            {
                "id": f"msg_{thread_id}_user_002",
                "threadId": thread_id,
                "role": "user",
                "content": "Ban co the giai thich ve AI khong?",
                "createdAt": datetime.utcnow().isoformat()
            },
            {
                "id": f"msg_{thread_id}_assistant_002",
                "threadId": thread_id,
                "role": "assistant",
                "content": "AI (Artificial Intelligence) la tri tue nhan tao - mot linh vuc khoa hoc may tinh tap trung vao viec tao ra cac he thong co the thuc hien cac tac vu thuong doi hoi tri thong minh cua con nguoi, nhu nhan dang giong noi, ra quyet dinh, va dich ngon ngu.",
                "createdAt": datetime.utcnow().isoformat()
            }
        ]
        
        # Insert messages
        for message in messages:
            await db.messages.insert_one(message)
        
        print(f"SUCCESS: Added {len(messages)} messages to thread {thread_id}")
        
        # Check data
        threads_count = await db.threads.count_documents({})
        messages_count = await db.messages.count_documents({})
        
        print(f"\nDatabase status:")
        print(f"   - Threads: {threads_count}")
        print(f"   - Messages: {messages_count}")
        
        print("\nSUCCESS: Sample data added successfully!")
        print("Now test Frontend to see if it loads the data...")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_data())
