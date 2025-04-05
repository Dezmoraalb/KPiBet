from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization


def get_dice_game_kb() -> InlineKeyboardMarkup:
    """Клавіатура для гри в кості"""
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🎲 Кинути кість",
        callback_data="dice:roll"
    )

    kb.button(
        text="⬅️ Назад",
        callback_data="main_menu"
    )

    kb.adjust(1, 1)
    
    return kb.as_markup()


def get_rps_game_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Клавіатура для гри камінь-ножиці-папір"""
    kb = InlineKeyboardBuilder()

    kb.button(
        text=l10n.format_value("rps-rock"),
        callback_data="rps:rock"
    )
    kb.button(
        text=l10n.format_value("rps-paper"),
        callback_data="rps:paper"
    )
    kb.button(
        text=l10n.format_value("rps-scissors"),
        callback_data="rps:scissors"
    )

    kb.button(
        text="⬅️ Назад",
        callback_data="main_menu"
    )

    kb.adjust(3, 1)
    
    return kb.as_markup()


def get_rps_webapp_kb(l10n: FluentLocalization):
    """Клавіатура для веб-додатку гри камінь-ножиці-папір"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=l10n.format_value("rps-webapp-button"),
                    web_app=WebAppInfo(url="https://illustrious-fenglisu-c771fe.netlify.app/")
                )
            ]
        ],
        resize_keyboard=True
    )

    return kb

def get_ttt_webapp_kb(l10n: FluentLocalization):
    """Клавіатура для веб-додатку гри камінь-ножиці-папір"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=l10n.format_value("rps-webapp-button"),
                    web_app=WebAppInfo(url="https://killsazer.github.io/React-TicTacToe/")
                )
            ]
        ],
        resize_keyboard=True
    )

    return kb

