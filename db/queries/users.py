from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from db.models.user import User, ChatMembership

# Користувачі

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """Отримати користувача за ID"""
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(
    session: AsyncSession,
    user_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str] = None,
    language_code: Optional[str] = None,
    invited_by: Optional[int] = None
) -> User:
    """Створити нового користувача"""
    user = User(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code,
        invited_by=invited_by
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_user_activity(session: AsyncSession, user_id: int) -> None:
    """Оновити час останньої активності користувача"""
    stmt = update(User).where(User.user_id == user_id).values(last_activity=func.now())
    await session.execute(stmt)
    await session.commit()

async def update_user_xp(session: AsyncSession, user_id: int, xp_delta: int) -> int:
    """Оновити XP користувача і повернути нове значення"""
    user = await get_user(session, user_id)
    if not user:
        return 0
        
    user.xp += xp_delta
    await session.commit()
    await session.refresh(user)
    return user.xp

async def update_user_bonuses(session: AsyncSession, user_id: int, bonus_delta: int) -> int:
    """Оновити бонуси користувача і повернути нове значення"""
    user = await get_user(session, user_id)
    if not user:
        return 0
        
    user.bonuses += bonus_delta
    await session.commit()
    await session.refresh(user)
    return user.bonuses

async def get_top_users(session: AsyncSession, limit: int = 3) -> List[User]:
    """Отримати топ користувачів за XP"""
    stmt = select(User).order_by(desc(User.xp)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_user_rank(session: AsyncSession, user_id: int) -> int:
    """Отримати позицію користувача в рейтингу"""
    user_xp_subquery = select(User.xp).where(User.user_id == user_id).scalar_subquery()

    stmt = select(func.count()).where(User.xp > user_xp_subquery)
    result = await session.execute(stmt)

    return result.scalar() + 1

# Чати

async def register_chat_member(
    session: AsyncSession, 
    user_id: int, 
    chat_id: int, 
    is_admin: bool = False
) -> ChatMembership:
    """Зареєструвати користувача як учасника чату"""
    stmt = select(ChatMembership).where(
        (ChatMembership.user_id == user_id) & 
        (ChatMembership.chat_id == chat_id)
    )
    result = await session.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if membership:
        membership.is_admin = is_admin
    else:
        membership = ChatMembership(
            user_id=user_id,
            chat_id=chat_id,
            is_admin=is_admin
        )
        session.add(membership)
    
    await session.commit()
    return membership

async def get_user_chats(session: AsyncSession, user_id: int) -> List[int]:
    """Отримати ідентифікатори всіх чатів, в яких бере участь користувач"""
    stmt = select(ChatMembership.chat_id).where(ChatMembership.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_referral_count(session: AsyncSession, user_id: int) -> int:
    """Отримати кількість запрошених користувачів"""
    stmt = select(func.count()).where(User.invited_by == user_id)
    result = await session.execute(stmt)
    return result.scalar()
