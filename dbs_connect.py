import os
import asyncpg

async def connect_to_db():
    try:
        
        DATABASE_URL = os.getenv("DATABASE_URL")

        
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set. Set it in your environment variables.")

        
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

