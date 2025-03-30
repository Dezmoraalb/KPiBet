from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization


def get_top_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура для відображення топу гравців"""
    kb = InlineKeyboardBuilder()

    kb.button(
        text=l10n.format_value("button-top-1"),
        callback_data="top:1"
    )
    kb.button(
        text=l10n.format_value("button-top-2"),
        callback_data="top:2"
    )
    kb.button(
        text=l10n.format_value("button-top-3"),
        callback_data="top:3"
    )

    kb.button(
        text=l10n.format_value("button-top-me"),
        callback_data="top:me"
    )

    kb.button(
        text=l10n.format_value("button-back"),
        callback_data="main_menu"
    )

    kb.adjust(3, 1, 1)
    
    return kb.as_markup()
