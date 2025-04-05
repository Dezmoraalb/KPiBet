import random
from typing import Tuple

class DiceGame:
    """
    Проста гра в кості.
    Кожен гравець отримує випадкове число від 1 до 6.
    Перемагає той, хто отримав більше число.
    """
    
    @staticmethod
    def roll_dice() -> int:
        """Підкинути кості (від 1 до 6)"""
        return random.randint(1, 6)
    
    @staticmethod
    def play_game() -> Tuple[int, int, str]:
        """
        Грати в гру.
        
        Returns:
            Tuple[int, int, str]: (число гравця, число бота, результат)
        """
        player_roll = DiceGame.roll_dice()
        bot_roll = DiceGame.roll_dice()
        
        if player_roll > bot_roll:
            result = "win"
        elif player_roll < bot_roll:
            result = "lose"
        else:
            result = "draw"
            
        return player_roll, bot_roll, result
    
    @staticmethod
    def calculate_reward(result: str) -> int:
        """
        Обчислити винагороду за гру.
        
        Args:
            result (str): результат гри ('win', 'lose', або 'draw')
            
        Returns:
            int: кількість XP, яку отримує користувач
        """
        if result == "win":
            return 10
        elif result == "draw":
            return 3
        else:
            return 1
