import unittest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.dice_game import DiceGame
from games.rps_game import RockPaperScissorsGame
from utils.game_tracker import GameTracker
from filters.chat_type import ChatTypeFilter


class TestDiceGame(unittest.TestCase):
    def test_roll_dice(self):
        result = DiceGame.roll_dice()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 6)
    
    def test_play_game(self):
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [4, 2]
            player_roll, bot_roll, result = DiceGame.play_game()
            
            self.assertEqual(player_roll, 4)
            self.assertEqual(bot_roll, 2)
            self.assertEqual(result, "win")
    
    def test_calculate_reward(self):
        win_reward = DiceGame.calculate_reward("win")
        draw_reward = DiceGame.calculate_reward("draw")
        lose_reward = DiceGame.calculate_reward("lose")
        
        self.assertEqual(win_reward, 10)
        self.assertEqual(draw_reward, 3)
        self.assertEqual(lose_reward, 1)


class TestRockPaperScissorsGame(unittest.TestCase):
    def test_get_bot_choice(self):
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "rock"
            choice = RockPaperScissorsGame.get_bot_choice()
            self.assertEqual(choice, "rock")
    
    def test_play_game_win(self):
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "scissors"

            player_choice, bot_choice, result = RockPaperScissorsGame.play_game("rock")
            
            self.assertEqual(player_choice, "rock")
            self.assertEqual(bot_choice, "scissors")
            self.assertEqual(result, "win")
    
    def test_play_game_lose(self):
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "paper"

            player_choice, bot_choice, result = RockPaperScissorsGame.play_game("rock")
            
            self.assertEqual(player_choice, "rock")
            self.assertEqual(bot_choice, "paper")
            self.assertEqual(result, "lose")
    
    def test_play_game_draw(self):
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "rock"

            player_choice, bot_choice, result = RockPaperScissorsGame.play_game("rock")
            
            self.assertEqual(player_choice, "rock")
            self.assertEqual(bot_choice, "rock")
            self.assertEqual(result, "draw")
    
    def test_play_game_invalid_choice(self):
        with patch('random.choice') as mock_choice:
            mock_choice.side_effect = ["paper", "rock"]

            player_choice, bot_choice, result = RockPaperScissorsGame.play_game("invalid")
            
            self.assertEqual(player_choice, "paper")
            self.assertEqual(bot_choice, "rock")
            self.assertEqual(result, "win")
    
    def test_calculate_reward(self):
        win_reward = RockPaperScissorsGame.calculate_reward("win")
        draw_reward = RockPaperScissorsGame.calculate_reward("draw")
        lose_reward = RockPaperScissorsGame.calculate_reward("lose")
        
        self.assertEqual(win_reward, 15)
        self.assertEqual(draw_reward, 5)
        self.assertEqual(lose_reward, 2)


class TestGameTracker(unittest.TestCase):
    def setUp(self):
        GameTracker._active_games = {}
    
    def test_start_game(self):
        result = GameTracker.start_game(123456789, "rps", 987654321)
        self.assertTrue(result)
        self.assertTrue(GameTracker.is_playing(123456789, "rps", 987654321))

        self.assertFalse(GameTracker.is_playing(123456789, "dice", 987654321))

        self.assertFalse(GameTracker.is_playing(123456789, "rps", 111111111))
    
    def test_end_game(self):
        GameTracker.start_game(123456789, "rps", 987654321)

        self.assertTrue(GameTracker.is_playing(123456789, "rps", 987654321))

        result = GameTracker.end_game(123456789, "rps", 987654321)
        self.assertTrue(result)

        self.assertFalse(GameTracker.is_playing(123456789, "rps", 987654321))


class TestChatTypeFilter(unittest.IsolatedAsyncioTestCase):
    async def test_private_chat_filter(self):
        message = MagicMock()
        message.chat.type = "private"
        
        filter_instance = ChatTypeFilter(chat_type="private")
        result = await filter_instance(message)
        
        self.assertTrue(result)
    
    async def test_group_chat_filter(self):
        message = MagicMock()
        message.chat.type = "private"
        
        filter_instance = ChatTypeFilter(chat_type="group")
        result = await filter_instance(message)
        
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
