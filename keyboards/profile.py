from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization


def get_profile_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура профілю користувача"""
    kb = InlineKeyboardBuilder()

    kb.button(
        text=l10n.format_value("button-referral"),
        callback_data="referral"
    )
    kb.button(
        text=l10n.format_value("button-settings"),
        callback_data="settings"
    )

    kb.button(
        text=l10n.format_value("button-bonuses"),
        callback_data="bonuses"
    )

    kb.button(
        text=l10n.format_value("button-back"),
        callback_data="main_menu"
    )

    kb.adjust(2, 1, 1)
    
    return kb.as_markup()
