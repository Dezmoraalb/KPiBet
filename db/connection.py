import asyncio
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config_reader import get_config, DatabaseConfig

db_config: DatabaseConfig = get_config(model=DatabaseConfig, root_key="database")

DATABASE_URL = f"postgresql+asyncpg://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}"

engine = create_async_engine(DATABASE_URL, echo=db_config.echo)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

logger = structlog.get_logger()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Створює асинхронну сесію бази даних.
    Використовується як залежність для функцій, які працюють з БД.
    """
    async with async_session_maker() as session:
        logger.debug("Created DB session")
        try:
            yield session
        finally:
            await session.close()
            logger.debug("Closed DB session")
