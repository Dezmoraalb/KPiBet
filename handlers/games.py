import json
import structlog
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, WebAppData, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization
from games.dice_game import DiceGame
from games.rps_game import RockPaperScissorsGame
from keyboards import get_dice_game_kb, get_main_menu_kb, get_rps_game_kb, get_rps_webapp_kb
from db.connection import get_async_session
from db.queries import get_user, update_user_xp, register_chat_member

router = Router()

logger = structlog.get_logger()


@router.message(Command("dice"))
async def cmd_dice_game(message: Message, l10n: FluentLocalization):
    """Обробник команди /dice для початку гри в кості"""
    await message.answer(
        l10n.format_value("dice-game-start"),
        reply_markup=get_dice_game_kb()
    )


@router.callback_query(F.data == "dice:roll")
async def callback_dice_roll(query: CallbackQuery, l10n: FluentLocalization):
    """Обробник натискання кнопки для кидання кості"""
    player_roll, bot_roll, result = DiceGame.play_game()

    xp_reward = DiceGame.calculate_reward(result)

    if result == "win":
        result_text = l10n.format_value("dice-game-win")
    elif result == "lose":
        result_text = l10n.format_value("dice-game-lose")
    else:
        result_text = l10n.format_value("dice-game-draw")

    async for session in get_async_session():
        await update_user_xp(session, query.from_user.id, xp_reward)

    await query.message.edit_text(
        l10n.format_value("dice-game-result", {
            "player_roll": player_roll,
            "bot_roll": bot_roll,
            "result_text": result_text,
            "xp": xp_reward
        }),
        reply_markup=get_dice_game_kb()
    )
    
    await query.answer()


@router.message(Command("rps"))
async def cmd_rps_game(message: Message, l10n: FluentLocalization):
    """Game Rock-Paper-Scissors"""
    await message.answer(
        l10n.format_value("rps-game-start"),
        reply_markup=get_rps_game_kb(l10n)
    )


@router.callback_query(F.data.startswith("rps:"))
async def callback_rps_choice(query: CallbackQuery, l10n: FluentLocalization):
    choice = query.data.split(":")[1]

    player_choice, bot_choice, result = RockPaperScissorsGame.play_game(choice)

    player_choice_text = l10n.format_value(f"rps-{player_choice}")
    bot_choice_text = l10n.format_value(f"rps-{bot_choice}")

    if result == "win":
        result_text = l10n.format_value("rps-game-win")
    elif result == "lose":
        result_text = l10n.format_value("rps-game-lose")
    else:
        result_text = l10n.format_value("rps-game-draw")

    xp_reward = RockPaperScissorsGame.calculate_reward(result)

    async for session in get_async_session():
        await update_user_xp(session, query.from_user.id, xp_reward)

    await query.message.edit_text(
        l10n.format_value("rps-game-result", {
            "player_choice": player_choice_text,
            "bot_choice": bot_choice_text,
            "result_text": result_text,
            "xp": xp_reward
        }),
        reply_markup=get_rps_game_kb(l10n)
    )
    
    await query.answer()


@router.callback_query(F.data == "game:dice")
async def callback_menu_dice(query: CallbackQuery, l10n: FluentLocalization):
    """Обробник виклику гри в кості з меню"""
    await query.message.edit_text(
        l10n.format_value("dice-game-start"),
        reply_markup=get_dice_game_kb()
    )
    await query.answer()


@router.callback_query(F.data == "game:rps")
async def callback_menu_rps(query: CallbackQuery, l10n: FluentLocalization):
    """Обробник виклику гри в камінь-ножиці-папір з меню"""
    await query.message.edit_text(
        l10n.format_value("rps-game-start"),
        reply_markup=get_rps_game_kb(l10n)
    )
    await query.answer()


@router.message(Command("rpc_app"))
async def cmd_rps_webapp_private(message: Message, l10n: FluentLocalization):
    """Обробник команди /rpc_app в чаті"""
    await message.answer(
        l10n.format_value("rps-webapp-start"),
        reply_markup=get_rps_webapp_kb(l10n)
    )


@router.message(Command("ttt_app"))
async def cmd_rps_webapp_private(message: Message, l10n: FluentLocalization):
    """Обробник команди /ttt_app в чаті"""
    await message.answer(
        l10n.format_value("rps-webapp-start"),
        reply_markup=get_rps_webapp_kb(l10n)
    )


@router.message(F.web_app_data)
async def process_webapp_data(message: Message, l10n: FluentLocalization):
    """Обробник для отримання данних з webapp"""
    web_app_data = message.web_app_data.data

    try:
        data = json.loads(web_app_data)
        player_count = data.get('playerCount', 0)

        if player_count > 0:
            result_text = l10n.format_value("rps-game-win")
            xp_reward = (player_count // 3) * 15
            if xp_reward == 0 and player_count > 0:
                xp_reward = 15
        elif player_count == 0:  # Если равно 0, то ничья
            result_text = l10n.format_value("rps-game-draw")
            xp_reward = 5
        else:
            result_text = l10n.format_value("rps-game-lose")
            xp_reward = (abs(player_count) // 2) * 2
            if xp_reward == 0:
                xp_reward = 2

        async for session in get_async_session():
            await update_user_xp(session, message.from_user.id, xp_reward)

        await message.answer(
            l10n.format_value("rps-webapp-result", {
                "score": abs(player_count),
                "result_text": result_text,
                "xp": xp_reward
            })
        )

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error processing web app data: {e}")
        await message.answer(
            l10n.format_value("rps-webapp-error")
        )


