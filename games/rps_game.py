import random
from typing import Tuple, Literal

class RockPaperScissorsGame:
    """
    Гра "Камінь, ножиці, папір".
    Користувач вибирає один з трьох варіантів, бот також робить випадковий вибір.
    Перемога визначається за стандартними правилами гри.
    """
    
    CHOICES = ["rock", "paper", "scissors"]
    
    @staticmethod
    def get_bot_choice() -> str:
        """Отримати випадковий вибір бота"""
        return random.choice(RockPaperScissorsGame.CHOICES)
    
    @staticmethod
    def play_game(player_choice: str) -> Tuple[str, str, Literal["win", "lose", "draw"]]:
        """
        Зіграти в гру.
        
        Args:
            player_choice (str): вибір гравця ('rock', 'paper', або 'scissors')
            
        Returns:
            Tuple[str, str, str]: (вибір гравця, вибір бота, результат)
        """
        player_choice = player_choice.lower()

        if player_choice not in RockPaperScissorsGame.CHOICES:
            player_choice = random.choice(RockPaperScissorsGame.CHOICES)

        bot_choice = RockPaperScissorsGame.get_bot_choice()

        if player_choice == bot_choice:
            result = "draw"
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            result = "win"
        else:
            result = "lose"
            
        return player_choice, bot_choice, result
    
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
            return 15
        elif result == "draw":
            return 5
        else:
            return 2
