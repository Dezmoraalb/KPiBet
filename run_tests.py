import unittest
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')

    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)

    print(f"\nВсього тестiв: {test_result.testsRun}")
    print(f"Успiшно: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}")
    print(f"Помилок: {len(test_result.errors)}")
    print(f"Провальних: {len(test_result.failures)}")

    sys.exit(len(test_result.failures) + len(test_result.errors))