from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from fluent.runtime import FluentLocalization


def get_settings_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура налаштувань"""
    builder = InlineKeyboardBuilder()
    
    # Основні налаштування
    builder.button(
        text="Сповіщення",
        callback_data="settings:notifications"
    )
    builder.button(
        text="Приватність",
        callback_data="settings:privacy"
    )
    
    # Додаткові опції
    builder.button(
        text="Статистика",
        callback_data="settings:stats"
    )
    builder.button(
        text="Досягнення", 
        callback_data="achievements"
    )
    builder.button(
        text="Щоденний бонус",
        callback_data="daily"
    )
    
    # Кнопка повернення
    builder.button(
        text="Назад",
        callback_data="main_menu"
    )
    
    # Розташування кнопок: 2 в ряд
    builder.adjust(2, 1, 1, 1, 1)
    
    return builder.as_markup()


def get_notification_settings_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура налаштувань сповіщень"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Увімкнути все",
        callback_data="notifications:all_on"
    )
    builder.button(
        text="Вимкнути все", 
        callback_data="notifications:all_off"
    )
    builder.button(
        text="Тільки ігри",
        callback_data="notifications:games_only"
    )
    builder.button(
        text="Тільки соціальні",
        callback_data="notifications:social_only"
    )
    builder.button(
        text="Назад",
        callback_data="settings"
    )
    
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_privacy_settings_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура налаштувань приватності"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Показувати профіль",
        callback_data="privacy:profile_public"
    )
    builder.button(
        text="Приховати профіль",
        callback_data="privacy:profile_private"
    )
    builder.button(
        text="Показувати статистику",
        callback_data="privacy:stats_public"
    )
    builder.button(
        text="Приховати статистику",
        callback_data="privacy:stats_private"
    )
    builder.button(
        text="Назад",
        callback_data="settings"
    )
    
    builder.adjust(2, 2, 1)
    return builder.as_markup()
