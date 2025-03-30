import structlog
import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import TelegramBadRequest

from fluent.runtime import FluentLocalization
from db.connection import get_async_session
from db.queries import register_chat_member, get_user, update_user_xp, get_top_users, create_user, get_user_rank
from games.dice_game import DiceGame
from games.rps_game import RockPaperScissorsGame
from utils.game_tracker import GameTracker

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

logger = structlog.get_logger()


@router.my_chat_member()
async def bot_added_to_group(event: ChatMemberUpdated, l10n: FluentLocalization = None):
    if l10n is None:
        logger.error("FluentLocalization object is missing in bot_added_to_group")
        welcome_text = "Привіт! Я ігровий бот. Використовуйте /help для детальної інформації."
    else:
        welcome_text = f"""👋 <b>Привіт, учасники чату {event.chat.title}!</b>
        
Я ігровий бот, який допоможе зробити ваше спілкування цікавішим! ⭐️
        
Доступні команди для чату:
/help - показати цей список команд
/dice - кинути кубик і отримати XP (відправте емоджі 🎲 у відповідь на команду)
/rps - зіграти в камінь-ножиці-папір (відправте емоджі 🤜, 🧳 або ✂️)
/profile - подивитись ваш профіль
/top - показати топ гравців
        
Почніть грати зараз і отримуйте XP! 🌟
Ваші досягнення будуть відображатись у рейтингу найкращих гравців чату."""
    
    if event.new_chat_member.status in ["member", "administrator"]:
        await event.bot.send_message(event.chat.id, welcome_text)
        logger.info(f"Bot added to chat {event.chat.id}")


@router.message(Command("help"))
async def cmd_help_in_group(message: Message, l10n: FluentLocalization):
    help_text = f"""📚 <b>Доступні команди в чаті:</b>

/help - показати цей список команд
/dice - кинути кубик і отримати XP (відправте емоджі 🎲 у відповідь на команду)
/rps - зіграти в камінь-ножиці-папір (відправте емоджі 🤜, 🧳 або ✂️)
/profile - подивитись ваш профіль (з фото профілю)
/top - показати топ гравців
/stats - показати статистику чату

<b>Як працюють ігри:</b>

🎲 <b>Кубик</b> - ви кидаєте емоджі кубика, бот також кидає. Перемагає той, у кого більше очків. Перемога: 10 XP, Нічия: 3 XP, Поразка: 1 XP.

🖐️ <b>Камінь-ножиці-папір</b> - ви відправляєте один з емоджі: 🤜 (камінь), 🧳 (папір) або ✂️ (ножиці). Перемога: 15 XP, Нічия: 5 XP, Поразка: 2 XP."""
    await message.reply(help_text)


@router.message(Command("stats"))
async def cmd_stats_in_group(message: Message, l10n: FluentLocalization):
    await message.answer("Статистика чату буде доступна незабаром!")


@router.message(Command("top"))
async def cmd_top_in_group(message: Message, l10n: FluentLocalization):
    async for session in get_async_session():
        top_users = await get_top_users(session, limit=3)

        text = f"🏆 <b>Топ гравців за XP:</b>\n\n"
        
        for i, user in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            text += f"{medal} {i}. {user.first_name} - {user.xp} XP\n"
        await message.reply(text)


@router.message(Command("profile"))
async def cmd_profile_in_group(message: Message, l10n: FluentLocalization, bot: Bot):
    user_id = message.from_user.id
    
    async for session in get_async_session():
        user = await get_user(session, user_id)
        if not user:
            user = await create_user(
                session,
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code
            )

        rank = await get_user_rank(session, user_id)

        profile_text = f"""👤 <b>Профіль користувача</b>

📛 Ім'я: {message.from_user.first_name}{f" {message.from_user.last_name}" if message.from_user.last_name else ""}
🆔 ID: {user_id}
💰 XP: {user.xp}
🎁 Бонуси: {user.bonuses}
🏆 Ваше місце в рейтингу: {rank}
⏳ Остання активність: {user.last_activity.strftime("%d.%m.%Y %H:%M")}
📅 Дата реєстрації: {user.created_at.strftime("%d.%m.%Y %H:%M")}"""

    try:
        user_photos = await bot.get_user_profile_photos(user_id, limit=1)
        if user_photos.total_count > 0:
            photo = user_photos.photos[0][-1]
            await message.reply_photo(photo.file_id, caption=profile_text)
        else:
            await message.reply(profile_text)
    except Exception as e:
        logger.error(f"Error getting profile photo: {e}")
        await message.reply(profile_text)


@router.message(Command("dice"))
async def cmd_dice_in_group(message: Message, l10n: FluentLocalization, bot: Bot):
    """Game of dice in group chat"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if GameTracker.is_playing(chat_id, "rps", user_id):
        return

    GameTracker.start_game(chat_id, "dice", user_id)

    prompt_message = await message.reply(
        f"""🎲 <b>Гра в кубик</b>
        
{message.from_user.first_name}, відправте емоджі кубика 🎲 у відповідь на це повідомлення, щоб кинути кубик."""
    )

    try:
        await asyncio.sleep(30)
        if GameTracker.is_playing(chat_id, "dice", user_id):
            GameTracker.end_game(chat_id, "dice", user_id)
            await prompt_message.delete()
    except Exception as e:
        logger.error(f"Error in dice game timeout: {e}")


@router.message(F.dice, F.reply_to_message)
async def handle_dice_game(message: Message, bot: Bot):
    """Handle dice emoji reply"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not message.reply_to_message or message.reply_to_message.from_user.id != bot.id or not GameTracker.is_playing(chat_id, "dice", user_id):
        return

    player_roll = message.dice.value

    bot_dice_message = await message.answer_dice(emoji="🎲")
    bot_roll = bot_dice_message.dice.value

    await asyncio.sleep(4)

    if player_roll > bot_roll:
        result = "win"
        result_text = "🎉 Ви перемогли!"
        xp_reward = 10
    elif player_roll < bot_roll:
        result = "lose"
        result_text = "😢 Ви програли, але все одно отримуєте невеликий бонус."
        xp_reward = 1
    else:  # draw
        result = "draw"
        result_text = "🤷 Нічия! Можете спробувати ще раз."
        xp_reward = 3

    async for session in get_async_session():
        new_xp = await update_user_xp(session, message.from_user.id, xp_reward)
        user = await get_user(session, message.from_user.id)
        if not user:
            await create_user(
                session,
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code
            )
            new_xp = xp_reward

    result_message = await message.reply(
        f"""🎲 <b>Результат гри в кубик:</b>

Ваш результат: {player_roll}
Результат бота: {bot_roll}

{result_text}

Ви отримуєте {xp_reward} XP! 🌟
Ваш загальний рахунок: {new_xp} XP"""
    )

    GameTracker.end_game(chat_id, "dice", user_id)

    await asyncio.sleep(20)
    try:
        await message.reply_to_message.delete()
        await message.delete()
        await bot_dice_message.delete()
        await result_message.delete()
    except Exception as e:
        logger.error(f"Error deleting dice game messages: {e}")


@router.message(Command("rps"))
async def cmd_rps_in_group(message: Message, l10n: FluentLocalization, bot: Bot):
    """Game Rock-Paper-Scissors in group chat"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if GameTracker.is_playing(chat_id, "dice", user_id):
        return

    GameTracker.start_game(chat_id, "rps", user_id)

    prompt_message = await message.reply(
        f"""🖐️ <b>Камінь-Ножиці-Папір</b>
        
{message.from_user.first_name}, відправте один з емоджі у відповідь на це повідомлення:
🤜 - Камінь
🧳 - Папір
✂️ - Ножиці"""
    )

    try:
        await asyncio.sleep(30)
        if GameTracker.is_playing(chat_id, "rps", user_id):
            GameTracker.end_game(chat_id, "rps", user_id)
            await prompt_message.delete()
    except Exception as e:
        logger.error(f"Error in RPS game timeout: {e}")


@router.message(F.text.in_(["🤜", "✂️", "🧳"]), F.reply_to_message)
async def handle_rps_game(message: Message, bot: Bot):
    """Handle rock-paper-scissors emoji reply"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not message.reply_to_message or message.reply_to_message.from_user.id != bot.id or not GameTracker.is_playing(chat_id, "rps", user_id):
        return

    player_choice_emoji = message.text
    player_choice = ""
    if player_choice_emoji == "🤜":
        player_choice = "rock"
        player_choice_text = "Камінь 🤜"
    elif player_choice_emoji == "🧳":
        player_choice = "paper"
        player_choice_text = "Папір 🧳"
    elif player_choice_emoji == "✂️":
        player_choice = "scissors"
        player_choice_text = "Ножиці ✂️"
    else:
        GameTracker.end_game(chat_id, "rps", user_id)
        return

    bot_choice = RockPaperScissorsGame.get_bot_choice()

    if bot_choice == "rock":
        bot_emoji = "🤜"
        bot_choice_text = "Камінь 🤜"
    elif bot_choice == "paper":
        bot_emoji = "🧳"
        bot_choice_text = "Папір 🧳"
    else:
        bot_emoji = "✂️"
        bot_choice_text = "Ножиці ✂️"

    bot_choice_message = await message.answer(bot_emoji)

    await asyncio.sleep(1)

    if player_choice == bot_choice:
        result_text = "🤷 Нічия! Можете спробувати ще раз."
        xp_reward = 5
    elif (
        (player_choice == "rock" and bot_choice == "scissors") or
        (player_choice == "paper" and bot_choice == "rock") or
        (player_choice == "scissors" and bot_choice == "paper")
    ):
        result_text = "🎉 Ви перемогли!"
        xp_reward = 15
    else:
        result_text = "😢 Ви програли, але все одно отримуєте невеликий бонус."
        xp_reward = 2

    async for session in get_async_session():
        new_xp = await update_user_xp(session, message.from_user.id, xp_reward)
        user = await get_user(session, message.from_user.id)
        if not user:
            await create_user(
                session,
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code
            )
            new_xp = xp_reward

    result_message = await message.reply(
        f"""🖐️ <b>Результат гри Камінь-Ножиці-Папір:</b>

Ваш вибір: {player_choice_text}
Вибір бота: {bot_choice_text}

{result_text}

Ви отримуєте {xp_reward} XP! 🌟
Ваш загальний рахунок: {new_xp} XP"""
    )

    GameTracker.end_game(chat_id, "rps", user_id)

    await asyncio.sleep(20)
    try:
        await message.reply_to_message.delete()
        await message.delete()
        await bot_choice_message.delete()
        await result_message.delete()
    except Exception as e:
        logger.error(f"Error deleting RPS game messages: {e}")


@router.message(F.new_chat_members)
async def new_members_handler(message: Message, l10n: FluentLocalization):
    for member in message.new_chat_members:
        if not member.is_bot:
            async for session in get_async_session():
                user = await get_user(session, member.id)
                if user:
                    await register_chat_member(session, member.id, message.chat.id)
                    await update_user_xp(session, member.id, 10)


@router.message(F.text)
async def process_group_message(message: Message):
    """
    Обробляє текстові повідомлення в групі.
    Можна додати логіку нарахування XP за активність.
    """
    async for session in get_async_session():
        user = await get_user(session, message.from_user.id)
        if user:
            await update_user_xp(session, message.from_user.id, 1)
            is_admin = False
            try:
                chat_member = await message.chat.get_member(message.from_user.id)
                is_admin = chat_member.status in ["administrator", "creator"]
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")

            await register_chat_member(
                session, 
                message.from_user.id, 
                message.chat.id,
                is_admin=is_admin
            )
