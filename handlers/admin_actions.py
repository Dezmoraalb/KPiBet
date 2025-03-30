import structlog
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from fluent.runtime import FluentLocalization
from db.connection import get_async_session
from db.queries import get_user, update_user_xp, update_user_bonuses

router = Router()

logger = structlog.get_logger()


@router.message(Command("ping"))
async def cmd_ping(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("ping-msg"))


@router.message(Command("add_xp"))
async def cmd_add_xp(message: Message, command: CommandObject, bot: Bot, l10n: FluentLocalization):
    try:
        bot_config = bot.config
        if message.from_user.id not in bot_config.owners:
            await message.answer("Ви не маєте прав для використання цієї команди.")
            return
    except (AttributeError, KeyError):
        await message.answer("Помилка отримання конфігурації бота.")
        return

    if not command.args:
        await message.answer("Використання: /add_xp <user_id> <amount>")
        return
    
    try:
        args = command.args.split()
        if len(args) != 2:
            await message.answer("Використання: /add_xp <user_id> <amount>")
            return
        
        user_id = int(args[0])
        amount = int(args[1])
        
        async for session in get_async_session():
            user = await get_user(session, user_id)
            if not user:
                await message.answer(f"Користувач з ID {user_id} не знайдений.")
                return
            
            new_xp = await update_user_xp(session, user_id, amount)
            await message.answer(f"Додано {amount} XP користувачу {user.first_name}. Новий баланс: {new_xp} XP")
            logger.info(f"Admin {message.from_user.id} added {amount} XP to user {user_id}")
    
    except ValueError:
        await message.answer("Помилка: ID користувача та кількість XP повинні бути числами.")
    except Exception as e:
        logger.error(f"Error in add_xp command: {e}")
        await message.answer(f"Виникла помилка: {e}")


@router.message(Command("add_bonus"))
async def cmd_add_bonus(message: Message, command: CommandObject, bot: Bot, l10n: FluentLocalization):
    try:
        bot_config = bot.config
        if message.from_user.id not in bot_config.owners:
            await message.answer("Ви не маєте прав для використання цієї команди.")
            return
    except (AttributeError, KeyError):
        await message.answer("Помилка отримання конфігурації бота.")
        return

    if not command.args:
        await message.answer("Використання: /add_bonus <user_id> <amount>")
        return
    
    try:
        args = command.args.split()
        if len(args) != 2:
            await message.answer("Використання: /add_bonus <user_id> <amount>")
            return
        
        user_id = int(args[0])
        amount = int(args[1])
        
        async for session in get_async_session():
            user = await get_user(session, user_id)
            if not user:
                await message.answer(f"Користувач з ID {user_id} не знайдений.")
                return
            
            new_bonuses = await update_user_bonuses(session, user_id, amount)
            await message.answer(f"Додано {amount} бонусів користувачу {user.first_name}. Новий баланс: {new_bonuses} бонусів")
            logger.info(f"Admin {message.from_user.id} added {amount} bonuses to user {user_id}")
    
    except ValueError:
        await message.answer("Помилка: ID користувача та кількість бонусів повинні бути числами.")
    except Exception as e:
        logger.error(f"Error in add_bonus command: {e}")
        await message.answer(f"Виникла помилка: {e}")
