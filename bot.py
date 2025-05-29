import asyncio
import sys

# Fix for Windows aiodns issue - MUST be at the very top
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_reader import get_config, BotConfig, LogConfig, DatabaseConfig
from logs import get_structlog_config
from structlog.typing import FilteringBoundLogger

from dispatcher import dp
import handlers
from db import init_database

async def main():
    # init logging
    log_config: LogConfig = get_config(model=LogConfig, root_key="logs")
    structlog.configure(**get_structlog_config(log_config))

    # get bot config
    bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
    
    # get database config
    db_config: DatabaseConfig = get_config(model=DatabaseConfig, root_key="database")

    # init logger
    logger: FilteringBoundLogger = structlog.get_logger()
    
    # init database
    await init_database()
    logger.info("Database initialized successfully")

    # init bot object
    bot = Bot(
        token=bot_config.token.get_secret_value(), # get token as secret, so it will be hidden in logs
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML # ParseMode (HTML or MARKDOWN_V2 is preferable)
        )
    )

    # start the logger
    await logger.ainfo("Starting the bot...")

    # start polling
    try:
        await dp.start_polling(bot, skip_updates=False) # Don't skip updates, if your bot will process payments or other important stuff
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
