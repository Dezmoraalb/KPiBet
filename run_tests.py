import unittest
import sys
import os

if __name__ == "__main__":
    # Настраиваем путь для импорта модулей проекта
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Загружаем все тесты из директории tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    
    # Запускаем тесты
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Выводим итоговую информацию
    print(f"\nВсього тестiв: {test_result.testsRun}")
    print(f"Успiшно: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}")
    print(f"Помилок: {len(test_result.errors)}")
    print(f"Провальних: {len(test_result.failures)}")
    
    # Устанавливаем код возврата
    sys.exit(len(test_result.failures) + len(test_result.errors))
