from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings 

class Database:
    client: AsyncIOMotorClient = None

db_instance = Database()

async def get_database():
    return db_instance.client[settings.database_name]
