import unittest
from unittest.mock import patch
from io import StringIO
import re
import textwrap

from t4th import t4th

class TestT4th(unittest.TestCase):
    _welcome_message_patter = pattern = r'T4th version (\d+\.\d+\.\d+) \[ Free memory (\d+) \]'

    def _assert_welcome_message(self, welcome_line):
        match = re.match(self._welcome_message_patter, welcome_line)
        self.assertIsNotNone(match, f"Welcome message is not matched: {welcome_line}")

    def _run_script(self, script_lines) -> str:
        if not script_lines.endswith('\n'):
            script_lines += '\n'

        with patch('sys.stdin', new=StringIO(script_lines)), \
             patch('sys.stdout', new=StringIO()) as mock_stdout:
            t4th.main()
            output = mock_stdout.getvalue()
            output_lines = output.split('\n')
            welcome_line = output_lines[0]
            self._assert_welcome_message(welcome_line)

            return '\n'.join([s.rstrip() for s in output_lines[1:]]).strip()

    def test_boot_and_bye(self):
        input_lines = "bye"
        expected_output_lines = "bye"

        output_lines = self._run_script(input_lines)
        self.assertEqual(output_lines, expected_output_lines)

    def test_basic_stack_operations(self):
        input_lines = textwrap.dedent("""
            .S
            1 2 3
            .S
            drop .S
            dup .S
            drop 4 swap .S
            over .S
        """).strip()

        expected_output_lines = textwrap.dedent("""
            .S <0>  ok
            1 2 3  ok
            .S <3> 1 2 3  ok
            drop .S <2> 1 2  ok
            dup .S <3> 1 2 2  ok
            drop 4 swap .S <3> 1 4 2  ok
            over .S <4> 1 4 2 4  ok
        """).strip()

        output_lines = self._run_script(input_lines)
        self.assertEqual(output_lines, expected_output_lines)

    def test_word_definition(self):
        input_lines = textwrap.dedent("""
            : square dup * ;
            : cube dup square * ;

            3 square . cr
            3 cube . cr

            bye
        """).strip()

        expected_output_lines = textwrap.dedent("""
            : square dup * ;  ok
            : cube dup square * ;  ok
              ok
            3 square . cr 9
             ok
            3 cube . cr 27
             ok
              ok
            bye
        """).strip()

        output_lines = self._run_script(input_lines)
        self.assertEqual(output_lines, expected_output_lines)

    def test_literal_related(self):
        input_lines = textwrap.dedent("""
            : test [ 42 ] literal ;
            test .
            bye
        """).strip()

        expected_output_lines = textwrap.dedent("""
            : test [ 42 ] literal ;  ok
            test . 42  ok
            bye
        """).strip()

        output_lines = self._run_script(input_lines)
        self.assertEqual(output_lines, expected_output_lines)

if __name__ == '__main__':
    unittest.main()
