import structlog
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from fluent.runtime import FluentLocalization
from keyboards import (
    get_main_menu_kb, get_profile_kb, get_top_kb, get_settings_kb,
    get_notification_settings_kb, get_privacy_settings_kb,
    get_games_menu_kb, get_webapp_games_kb
)
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
async def cmd_start(message: Message, l10n: FluentLocalization, command: CommandObject = None):
    async for session in get_async_session():
        user = await get_user(session, message.from_user.id)
        
        # Handle referral links
        referrer_id = None
        if command and command.args and command.args.startswith("ref_"):
            try:
                referrer_id = int(command.args.split("_")[1])
                referrer = await get_user(session, referrer_id)
                if referrer and referrer_id != message.from_user.id:
                    # Give bonus to referrer
                    await update_user_xp(session, referrer_id, 50)
                    logger.info(f"Referrer {referrer_id} got 50 XP for inviting {message.from_user.id}")
            except (ValueError, IndexError):
                referrer_id = None

        if not user:
            user = await create_user(
                session,
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                referred_by=referrer_id
            )
            logger.info(f"Created new user: {user.user_id}")
            
            if referrer_id:
                welcome_text = l10n.format_value("hello-referral-msg", {
                    "name": message.from_user.first_name,
                    "referrer_bonus": 50
                })
            else:
                welcome_text = l10n.format_value("hello-new-user-msg", {"name": message.from_user.first_name})
        else:
            await update_user_activity(session, message.from_user.id)
            welcome_text = l10n.format_value("hello-msg", {"name": message.from_user.first_name})

    await message.answer(
        welcome_text,
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
async def callback_referral(query: CallbackQuery, l10n: FluentLocalization, bot: Bot):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{query.from_user.id}"

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
    from sqlalchemy import text
    
    async for session in get_async_session():
        top_users = await get_top_users(session, limit=10)
        user_rank = await get_user_rank(session, user_id)
        total_users = await session.execute(text("SELECT COUNT(*) FROM users"))
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
        for i, user in enumerate(top_users[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            top_text += f"{medal} {i}. {user.first_name} - {user.xp} XP\n"
        
        top_text += "\n" + l10n.format_value('top-your-position', {
            "position": user_rank,
            "total": total_users
        })

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


@router.message(Command("settings"))
async def cmd_settings(message: Message, l10n: FluentLocalization):
    """Налаштування користувача"""
    await message.answer(
        l10n.format_value("settings-msg"),
        reply_markup=get_settings_kb(l10n)
    )


@router.callback_query(F.data == "settings")
async def callback_settings(query: CallbackQuery, l10n: FluentLocalization):
    """Відображення налаштувань"""
    await query.message.edit_text(
        l10n.format_value("settings-msg"),
        reply_markup=get_settings_kb(l10n)
    )
    await query.answer()


@router.callback_query(F.data == "achievements")
async def callback_achievements(query: CallbackQuery, l10n: FluentLocalization):
    """Відображення досягнень користувача"""
    async for session in get_async_session():
        user = await get_user(session, query.from_user.id)
        if not user:
            await query.answer("Помилка: користувач не знайдений")
            return
        
        # Простий список досягнень на основі XP
        achievements = []
        
        if user.xp >= 10:
            achievements.append("🎯 Новачок (10+ XP)")
        if user.xp >= 50:
            achievements.append("⭐ Активний гравець (50+ XP)")
        if user.xp >= 100:
            achievements.append("🔥 Досвідчений (100+ XP)")
        if user.xp >= 250:
            achievements.append("💎 Експерт (250+ XP)")
        if user.xp >= 500:
            achievements.append("👑 Майстер (500+ XP)")
        if user.xp >= 1000:
            achievements.append("🏆 Легенда (1000+ XP)")
        
        # Досягнення по рефералам
        ref_count = await get_referral_count(session, query.from_user.id)
        if ref_count >= 1:
            achievements.append("🤝 Запрошував друзів (1+ реферал)")
        if ref_count >= 5:
            achievements.append("👥 Популярний (5+ рефералів)")
        if ref_count >= 10:
            achievements.append("🌟 Лідер спільноти (10+ рефералів)")
        
        achievements_text = l10n.format_value("achievements-title") + "\n\n"
        if achievements:
            achievements_text += "\n".join(achievements)
        else:
            achievements_text += l10n.format_value("achievements-none")
        
        achievements_text += f"\n\n{l10n.format_value('achievements-stats-title')}\n💰 XP: {user.xp}\n🎁 Бонуси: {user.bonuses}\n👥 Запрошено друзів: {ref_count}"
    
    await query.message.edit_text(
        achievements_text,
        reply_markup=get_profile_kb(l10n)
    )
    await query.answer()


@router.message(Command("help"))
async def cmd_help(message: Message, l10n: FluentLocalization):
    """Довідка по командах бота"""
    help_text = """📚 <b>Доступні команди:</b>

🏠 /start - Головне меню
👤 /profile - Ваш профіль
🏆 /top - Топ гравців
🎮 /dice - Гра в кості
🖐️ /rps - Камінь-ножиці-папір
⚙️ /settings - Налаштування
🆘 /help - Ця довідка
📖 /about - Про бота

<b>Як отримувати XP:</b>
• Грайте в ігри (10-15 XP за перемогу)
• Запрошуйте друзів (50 XP за кожного)
• Будьте активними в чатах (1 XP за повідомлення)

<b>Бонуси можна витрачати на:</b>
• Прискорення відновлення енергії
• Додаткові спроби в іграх
• Унікальні досягнення

Для отримання додаткової інформації використовуйте кнопки меню! 🎯"""
    
    await message.answer(
        help_text,
        reply_markup=get_main_menu_kb(l10n)
    )


@router.callback_query(F.data == "help")
async def callback_help(query: CallbackQuery, l10n: FluentLocalization):
    """Довідка через callback"""
    help_text = """📚 <b>Доступні команди:</b>

🏠 Головне меню - повернутися до початку
👤 Профіль - переглянути свої дані
🏆 Топ - рейтинг найкращих гравців
🎮 Ігри - розваги та заробіток XP
⚙️ Налаштування - персоналізація
🆘 Довідка - ця інформація
📖 Про бота - детальна інформація

<b>Як працюють ігри:</b>
🎲 Кості - кидайте кубик проти бота
🖐️ Камінь-ножиці-папір - класична гра

<b>Система нагород:</b>
🥇 Перемога: 10-15 XP
🤝 Нічия: 3-5 XP  
😔 Поразка: 1-2 XP
👥 Реферал: 50 XP

Грайте, запрошуйте друзів та ставайте найкращими! 🌟"""
    
    await query.message.edit_text(
        help_text,
        reply_markup=get_main_menu_kb(l10n)
    )
    await query.answer()


@router.message(Command("daily"))
async def cmd_daily_bonus(message: Message, l10n: FluentLocalization):
    """Щоденний бонус"""
    async for session in get_async_session():
        user = await get_user(session, message.from_user.id)
        if not user:
            await message.answer(l10n.format_value("daily-bonus-register-first"))
            return
        
        # Перевіряємо, чи можна отримати щоденний бонус
        from datetime import datetime, timedelta
        now = datetime.now()
        
        # Якщо користувач ще не отримував бонус сьогодні
        if user.last_daily_bonus is None or (now - user.last_daily_bonus).days >= 1:
            daily_bonus = 25
            await update_user_xp(session, message.from_user.id, daily_bonus)
            
            # Оновлюємо час останнього отримання бонусу (тут потрібно додати це поле в модель)
            # await update_user_daily_bonus(session, message.from_user.id, now)
            
            await message.answer(
                l10n.format_value("daily-bonus-received", {
                    "bonus": daily_bonus,
                    "total": user.xp + daily_bonus
                }),
                reply_markup=get_main_menu_kb(l10n)
            )
        else:
            hours_left = 24 - (now - user.last_daily_bonus).seconds // 3600
            await message.answer(
                l10n.format_value("daily-bonus-already-claimed", {
                    "hours": hours_left
                }),
                reply_markup=get_main_menu_kb(l10n)
            )


@router.callback_query(F.data == "daily")
async def callback_daily_bonus(query: CallbackQuery, l10n: FluentLocalization):
    """Щоденний бонус через callback"""
    await cmd_daily_bonus(query.message, l10n)
    await query.answer()


# Хендлери для налаштувань
@router.callback_query(F.data.startswith("settings:"))
async def callback_settings_menu(query: CallbackQuery, l10n: FluentLocalization):
    """Обробка різних розділів налаштувань"""
    setting_type = query.data.split(":")[1]
    
    if setting_type == "notifications":
        await query.message.edit_text(
            "<b>🔔 Налаштування сповіщень</b>\n\n"
            "Оберіть, які сповіщення ви хочете отримувати:",
            reply_markup=get_notification_settings_kb(l10n)
        )
    elif setting_type == "language":
        await query.message.edit_text(
            "<b>🌐 Вибір мови</b>\n\n"
            "Оберіть зручну для вас мову інтерфейсу:",
            reply_markup=get_language_settings_kb(l10n)
        )
    elif setting_type == "privacy":
        await query.message.edit_text(
            "<b>📊 Налаштування приватності</b>\n\n"
            "Керуйте видимістю вашого профілю та статистики:",
            reply_markup=get_privacy_settings_kb(l10n)
        )
    elif setting_type == "theme":
        await query.message.edit_text(
            "<b>🎨 Вибір теми</b>\n\n"
            "Виберіть тему оформлення (поки недоступно):\n"
            "• 🌙 Темна тема\n"
            "• ☀️ Світла тема\n"
            "• 🌈 Кольорова тема",
            reply_markup=get_settings_kb(l10n)
        )
    elif setting_type == "stats":
        async for session in get_async_session():
            user = await get_user(session, query.from_user.id)
            if user:
                days_registered = (datetime.now() - user.created_at).days
                avg_xp_per_day = user.xp / max(days_registered, 1)
                
                stats_text = f"""<b>📈 Детальна статистика</b>

<b>👤 Профіль:</b>
• ID: {user.user_id}
• Реєстрація: {format_datetime(user.created_at)}
• Днів з нами: {days_registered}

<b>💰 XP та активність:</b>
• Загальний XP: {user.xp}
• Середній XP на день: {avg_xp_per_day:.1f}
• Бонуси: {user.bonuses}
• Остання активність: {format_datetime(user.last_activity)}

<b>👥 Соціальна активність:</b>
• Запрошено друзів: {await get_referral_count(session, query.from_user.id)}
• Позиція в рейтингу: {await get_user_rank(session, query.from_user.id)}

<b>🎮 Ігрова статистика:</b>
• Загальні ігри: скоро...
• Перемоги: скоро...
• Поразки: скоро..."""
                
                await query.message.edit_text(
                    stats_text,
                    reply_markup=get_settings_kb(l10n)
                )
    
    await query.answer()


@router.callback_query(F.data.startswith("notifications:"))
async def callback_notifications_settings(query: CallbackQuery, l10n: FluentLocalization):
    """Обробка налаштувань сповіщень"""
    action = query.data.split(":")[1]
    
    if action == "all_on":
        message_text = "🔔 Всі сповіщення увімкнені!"
    elif action == "all_off":
        message_text = "🔕 Всі сповіщення вимкнені!"
    elif action == "games_only":
        message_text = "🎮 Увімкнені тільки ігрові сповіщення!"
    elif action == "social_only":
        message_text = "👥 Увімкнені тільки соціальні сповіщення!"
    else:
        message_text = "⚙️ Налаштування збережені!"
    
    await query.answer(message_text, show_alert=True)
    await query.message.edit_text(
        "<b>🔔 Налаштування сповіщень</b>\n\n"
        f"{message_text}\n\n"
        "Оберіть, які сповіщення ви хочете отримувати:",
        reply_markup=get_notification_settings_kb(l10n)
    )


@router.callback_query(F.data.startswith("language:"))
async def callback_language_settings(query: CallbackQuery, l10n: FluentLocalization):
    """Обробка зміни мови"""
    language = query.data.split(":")[1]
    
    language_names = {
        "uk": "🇺🇦 Українська",
        "ru": "🇷🇺 Русский", 
        "en": "🇺🇸 English"
    }
    
    selected_language = language_names.get(language, "🇺🇦 Українська")
    
    # Тут можна додати логіку збереження мови в базі даних
    # await update_user_language(session, query.from_user.id, language)
    
    await query.answer(f"Обрано мову: {selected_language}", show_alert=True)
    await query.message.edit_text(
        "<b>🌐 Вибір мови</b>\n\n"
        f"Поточна мова: {selected_language}\n\n"
        "Оберіть зручну для вас мову інтерфейсу:",
        reply_markup=get_language_settings_kb(l10n)
    )


@router.callback_query(F.data == "games_menu")
async def callback_games_menu(query: CallbackQuery, l10n: FluentLocalization):
    """Меню ігор"""
    
    games_text = l10n.format_value("games-menu-title") + "\n\n" + \
                 l10n.format_value("games-dice-description") + "\n" + \
                 l10n.format_value("games-rps-description") + "\n" + \
                 l10n.format_value("games-webapp-description") + "\n\n" + \
                 l10n.format_value("games-rewards-info")
    
    await query.message.edit_text(
        games_text,
        reply_markup=get_games_menu_kb(l10n)
    )
    await query.answer()


@router.callback_query(F.data.startswith("privacy:"))
async def callback_privacy_settings(query: CallbackQuery, l10n: FluentLocalization):
    """Обробка налаштувань приватності"""
    privacy_type = query.data.split(":")[1]
    
    if privacy_type == "profile_public":
        message_text = "👁️ Профіль тепер публічний!"
    elif privacy_type == "profile_private":
        message_text = "🕶️ Профіль тепер приватний!"
    elif privacy_type == "stats_public":
        message_text = "📊 Статистика тепер видима всім!"
    elif privacy_type == "stats_private":
        message_text = "📊 Статистика тепер прихована!"
    else:
        message_text = "⚙️ Налаштування збережені!"
    
    # Тут можна додати логіку збереження налаштувань приватності в базі даних
    # await update_user_privacy_settings(session, query.from_user.id, privacy_type)
    
    await query.answer(message_text, show_alert=True)
    await query.message.edit_text(
        "<b>📊 Налаштування приватності</b>\n\n"
        f"{message_text}\n\n"
        "Керуйте видимістю вашого профілю та статистики:",
        reply_markup=get_privacy_settings_kb(l10n)
    )


@router.callback_query(F.data == "games:webapp")
async def callback_webapp_games(query: CallbackQuery, l10n: FluentLocalization):
    """Меню веб-ігор"""
    
    webapp_text = l10n.format_value("webapp-games-title") + "\n\n" + \
                  l10n.format_value("webapp-rps-description") + "\n" + \
                  l10n.format_value("webapp-ttt-description") + "\n\n" + \
                  l10n.format_value("webapp-bonus-info")
    
    await query.message.edit_text(
        webapp_text,
        reply_markup=get_webapp_games_kb(l10n)
    )
    await query.answer()


@router.callback_query(F.data.startswith("webapp:"))
async def callback_webapp_launch(query: CallbackQuery, l10n: FluentLocalization):
    """Запуск веб-додатків"""
    from keyboards.games import get_rps_webapp_kb, get_ttt_webapp_kb
    
    webapp_type = query.data.split(":")[1]
    
    if webapp_type == "rps":
        await query.message.answer(
            l10n.format_value("rps-webapp-start"),
            reply_markup=get_rps_webapp_kb(l10n)
        )
    elif webapp_type == "ttt":
        await query.message.answer(
            l10n.format_value("ttt-webapp-start"),
            reply_markup=get_ttt_webapp_kb(l10n)
        )
    
    await query.answer()


@router.callback_query(F.data == "my_bonuses")
async def callback_my_bonuses(query: CallbackQuery, l10n: FluentLocalization):
    """Відображення бонусів користувача"""
    async for session in get_async_session():
        user = await get_user(session, query.from_user.id)
        if not user:
            await query.answer("Помилка: користувач не знайдений")
            return
        
        bonuses_text = l10n.format_value("my-bonuses-info", {
            "bonuses": user.bonuses,
            "xp": user.xp
        })
    
    await query.message.edit_text(
        bonuses_text,
        reply_markup=get_profile_kb(l10n)
    )
    await query.answer()


@router.callback_query(F.data == "top")
async def callback_top_menu(query: CallbackQuery, l10n: FluentLocalization):
    """Відображення топу через callback"""
    await show_top(query.from_user.id, query.message, l10n, position=1, is_edit=True)
    await query.answer()

