import structlog
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from fluent.runtime import FluentLocalization
from keyboards import get_main_menu_kb, get_profile_kb, get_top_kb
from db.connection import get_async_session
from db.queries import (
    get_user, create_user, update_user_activity, 
    get_top_users, get_user_rank, get_referral_count
)


router = Router()
router.message.filter(F.chat.type == "private")


logger = structlog.get_logger()


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


@router.message(CommandStart())
async def cmd_start(message: Message, l10n: FluentLocalization):
    async for session in get_async_session():
        user = await get_user(session, message.from_user.id)

        if not user:
            user = await create_user(
                session,
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code
            )
            logger.info(f"Created new user: {user.user_id}")
        else:
            await update_user_activity(session, message.from_user.id)

    await message.answer(
        l10n.format_value("hello-msg", {"name": message.from_user.first_name}),
        reply_markup=get_main_menu_kb(l10n)
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message, l10n: FluentLocalization, bot: Bot):
    await show_profile(message.from_user.id, message, l10n, bot)


@router.message(Command("top"))
async def cmd_top(message: Message, l10n: FluentLocalization):
    await show_top(message.from_user.id, message, l10n, position=1)


@router.message(Command("about"))
async def cmd_about(message: Message, l10n: FluentLocalization):
    await message.answer(
        l10n.format_value("about-bot"),
        reply_markup=get_main_menu_kb(l10n)
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(query: CallbackQuery, l10n: FluentLocalization):
    await query.message.edit_text(
        l10n.format_value("hello-msg", {"name": query.from_user.first_name}),
        reply_markup=get_main_menu_kb(l10n)
    )
    await query.answer()

@router.callback_query(F.data == "profile")
async def callback_profile(query: CallbackQuery, l10n: FluentLocalization, bot: Bot):
    await show_profile(query.from_user.id, query.message, l10n, bot, is_edit=True)
    await query.answer()


@router.callback_query(F.data == "about")
async def callback_about(query: CallbackQuery, l10n: FluentLocalization):
    await query.message.edit_text(
        l10n.format_value("about-bot"),
        reply_markup=get_main_menu_kb(l10n)
    )
    await query.answer()


@router.callback_query(F.data.startswith("top:"))
async def callback_top(query: CallbackQuery, l10n: FluentLocalization):
    position = query.data.split(":")[1]
    if position == "me":
        position = 0
    else:
        position = int(position)
    
    await show_top(query.from_user.id, query.message, l10n, position=position, is_edit=True)
    await query.answer()


@router.callback_query(F.data == "referral")
async def callback_referral(query: CallbackQuery, l10n: FluentLocalization):
    ref_link = f"https://t.me/your_bot_username?start=ref_{query.from_user.id}"

    async for session in get_async_session():
        ref_count = await get_referral_count(session, query.from_user.id)
    
    await query.message.edit_text(
        l10n.format_value("referral-info", {
            "link": ref_link,
            "count": ref_count
        }),
        reply_markup=get_profile_kb(l10n)
    )
    await query.answer()


async def show_profile(user_id: int, message_or_query, l10n: FluentLocalization, bot: Bot, is_edit=False):
    """Відображення профілю користувача"""
    async for session in get_async_session():
        user = await get_user(session, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return

        rank = await get_user_rank(session, user_id)

        referrals = await get_referral_count(session, user_id)

    profile_text = l10n.format_value("profile-info", {
        "name": user.first_name + (f" {user.last_name}" if user.last_name else ""),
        "user_id": user.user_id,
        "xp": user.xp,
        "bonuses": user.bonuses,
        "referrals": referrals,
        "last_activity": format_datetime(user.last_activity),
        "registered_at": format_datetime(user.created_at),
        "rank": rank
    })

    try:
        user_photos = await bot.get_user_profile_photos(user_id, limit=1)
        has_photo = user_photos.total_count > 0
    except Exception as e:
        logger.error(f"Error getting profile photo: {e}")
        has_photo = False

    if is_edit:
        await message_or_query.edit_text(
            profile_text,
            reply_markup=get_profile_kb(l10n)
        )
    else:
        if has_photo:
            photo = user_photos.photos[0][-1]
            await message_or_query.answer_photo(
                photo.file_id,
                caption=profile_text,
                reply_markup=get_profile_kb(l10n)
            )
        else:
            await message_or_query.answer(
                profile_text,
                reply_markup=get_profile_kb(l10n)
            )


async def show_top(user_id: int, message_or_query, l10n: FluentLocalization, position=1, is_edit=False):
    """Відображення топу гравців"""
    async for session in get_async_session():
        top_users = await get_top_users(session, limit=3)
        user_rank = await get_user_rank(session, user_id)
        total_users = await session.execute("SELECT COUNT(*) FROM users")
        total_users = total_users.scalar()
    
    if position == 0:
        user = await get_user(session, user_id)
        top_text = f"{l10n.format_value('top-players-title')}\n\n"
        top_text += l10n.format_value('top-player-item', {
            "position": user_rank,
            "name": user.first_name,
            "xp": user.xp
        })
        top_text += "\n\n" + l10n.format_value('top-your-position', {
            "position": user_rank,
            "total": total_users
        })
    else:
        top_text = f"{l10n.format_value('top-players-title')}\n\n"
        if 1 <= position <= len(top_users):
            user = top_users[position - 1]
            top_text += l10n.format_value('top-player-item', {
                "position": position,
                "name": user.first_name,
                "xp": user.xp
            })
            top_text += "\n\n" + l10n.format_value('top-your-position', {
                "position": user_rank,
                "total": total_users
            })
        else:
            top_text += "Немає даних для відображення"

    if is_edit:
        await message_or_query.edit_text(
            top_text,
            reply_markup=get_top_kb(l10n)
        )
    else:
        await message_or_query.answer(
            top_text,
            reply_markup=get_top_kb(l10n)
        )

