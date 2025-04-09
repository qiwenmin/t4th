import unittest
from unittest.mock import patch
from io import StringIO
import re

from t4th import t4th

class TestT4th(unittest.TestCase):
    _welcome_message_patter = pattern = r'T4th version (\d+\.\d+\.\d+) \[ Free memory (\d+) \]'

    def _assert_welcome_message(self, welcome_line):
        match = re.match(self._welcome_message_patter, welcome_line)
        self.assertIsNotNone(match, f"Welcome message is not matched: {welcome_line}")

    def test_boot_and_bye(self):

        input_lines = "bye\n"

        with patch('sys.stdin', new=StringIO(input_lines)), \
             patch('sys.stdout', new=StringIO()) as mock_stdout:
            t4th.main()
            output = mock_stdout.getvalue()
            self._assert_welcome_message(output.split('\n')[0])

if __name__ == '__main__':
    unittest.main()
