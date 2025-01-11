import asyncpg

async def connect_to_db():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='mitsutech',
            database='postgres',
            host='localhost',
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
