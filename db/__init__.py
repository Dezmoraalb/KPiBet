import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.schema import CreateTable
from sqlalchemy import text

from db.models import Base
from db.models.user import User, ChatMembership
from db.connection import engine, async_session_maker

logger = structlog.get_logger()

async def create_tables():
    """Створення всіх таблиць в базі даних"""
    async with engine.begin() as conn:
        await conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
        
    logger.info("Database tables created successfully")

async def init_database():
    """Ініціалізація бази даних"""
    try:
        await create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
