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
        text="🎁 Мої бонуси",
        callback_data="my_bonuses"
    )

    kb.button(
        text=l10n.format_value("button-settings"),
        callback_data="settings"
    )

    kb.button(
        text=l10n.format_value("button-back"),
        callback_data="main_menu"
    )

    kb.adjust(2, 2)
    
    return kb.as_markup()
