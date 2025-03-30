from typing import Dict, Set

class GameTracker:
    """
    Клас для відстеження активних ігор в чатах.
    Використовується для обмеження доступу до гри тільки користувачу, який її розпочав.
    """
    _active_games: Dict[int, Dict[str, Set[int]]] = {}

    @classmethod
    def start_game(cls, chat_id: int, game_type: str, user_id: int) -> bool:
        """
        Розпочинає нову гру для користувача.
        
        Args:
            chat_id (int): ID чату
            game_type (str): Тип гри ('dice', 'rps', тощо)
            user_id (int): ID користувача
            
        Returns:
            bool: True, якщо гра успішно розпочата
        """
        if chat_id not in cls._active_games:
            cls._active_games[chat_id] = {}
        
        if game_type not in cls._active_games[chat_id]:
            cls._active_games[chat_id][game_type] = set()

        cls._active_games[chat_id][game_type].add(user_id)
        return True
    
    @classmethod
    def end_game(cls, chat_id: int, game_type: str, user_id: int) -> bool:
        """
        Завершує гру для користувача.
        
        Args:
            chat_id (int): ID чату
            game_type (str): Тип гри ('dice', 'rps', тощо)
            user_id (int): ID користувача
            
        Returns:
            bool: True, якщо гра успішно завершена
        """
        if (chat_id in cls._active_games and 
            game_type in cls._active_games[chat_id] and 
            user_id in cls._active_games[chat_id][game_type]):
            
            cls._active_games[chat_id][game_type].remove(user_id)
            
            # Видаляємо порожні набори
            if not cls._active_games[chat_id][game_type]:
                del cls._active_games[chat_id][game_type]
            
            # Видаляємо порожні словники чатів
            if not cls._active_games[chat_id]:
                del cls._active_games[chat_id]
                
            return True
        
        return False
    
    @classmethod
    def is_playing(cls, chat_id: int, game_type: str, user_id: int) -> bool:
        """
        Перевіряє, чи грає користувач у вказану гру в чаті.
        
        Args:
            chat_id (int): ID чату
            game_type (str): Тип гри ('dice', 'rps', тощо)
            user_id (int): ID користувача
            
        Returns:
            bool: True, якщо користувач зараз грає
        """
        return (chat_id in cls._active_games and 
                game_type in cls._active_games[chat_id] and 
                user_id in cls._active_games[chat_id][game_type])
