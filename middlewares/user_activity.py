from typing import Callable, Dict, Any, Awaitable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_async_session
from db.queries import get_user, update_user_activity, create_user


class UserActivityMiddleware(BaseMiddleware):
    """
    Middleware для відстеження активності користувачів.
    Оновлює час останньої активності користувача при кожній взаємодії з ботом.
    Також створює запис про користувача, якщо його ще немає в базі даних.
    """
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Отримуємо дані користувача
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            # Якщо тип події не підтримується, просто пропускаємо
            return await handler(event, data)
        
        # Отримуємо логер
        logger = structlog.get_logger()
        
        # Оновлюємо активність у БД
        async for session in get_async_session():
            try:
                # Перевіряємо, чи існує користувач
                existing_user = await get_user(session, user.id)
                
                if existing_user:
                    # Оновлюємо час активності користувача
                    await update_user_activity(session, user.id)
                else:
                    # Створюємо нового користувача, якщо його ще немає
                    await create_user(
                        session,
                        user_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code
                    )
                    logger.info(f"Created new user from middleware: {user.id}")
            except Exception as e:
                logger.error(f"Error updating user activity: {e}")
        
        # Продовжуємо обробку події
        return await handler(event, data)
