from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization


def get_main_menu_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Головне меню бота"""
    kb = InlineKeyboardBuilder()

    kb.button(
        text=l10n.format_value("button-add-to-chat"),
        url="https://t.me/KPiBet_bot?startgroup=new"
    )

    kb.button(
        text=l10n.format_value("button-profile"),
        callback_data="profile"
    )
    kb.button(
        text=l10n.format_value("button-top"),
        callback_data="top"
    )
    kb.button(
        text=l10n.format_value("button-about"),
        callback_data="about"
    )

    kb.adjust(1, 2, 1)
    
    return kb.as_markup()
