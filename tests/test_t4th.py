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

    def _run_script(self, script_lines, expected_output_lines):
        script_lines = textwrap.dedent(script_lines).strip() + '\n'

        expected_output_lines = textwrap.dedent(expected_output_lines).strip()

        with patch('sys.stdin', new=StringIO(script_lines)), \
             patch('sys.stdout', new=StringIO()) as mock_stdout:
            t4th.main()
            output = mock_stdout.getvalue()
            output_lines = output.split('\n')
            welcome_line = output_lines[0]
            self._assert_welcome_message(welcome_line)

            output_lines = '\n'.join([s.rstrip() for s in output_lines[1:]]).strip()
            self.assertEqual(output_lines, expected_output_lines)

    def test_boot_and_bye(self):
        input_lines = "bye"
        expected_output_lines = "bye"

        self._run_script(input_lines, expected_output_lines)

    def test_basic_stack_operations(self):
        input_lines = """
            .S
            1 2 3
            .S
            drop .S
            dup .S
            drop 4 swap .S
            over .S
        """

        expected_output_lines = """
            .S <0>  ok
            1 2 3  ok
            .S <3> 1 2 3  ok
            drop .S <2> 1 2  ok
            dup .S <3> 1 2 2  ok
            drop 4 swap .S <3> 1 4 2  ok
            over .S <4> 1 4 2 4  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_word_definition(self):
        input_lines = """
            : square dup * ;
            : cube dup square * ;

            3 square . cr
            3 cube . cr

            bye
        """

        expected_output_lines = """
            : square dup * ;  ok
            : cube dup square * ;  ok
              ok
            3 square . cr 9
             ok
            3 cube . cr 27
             ok
              ok
            bye
        """

        self._run_script(input_lines, expected_output_lines)

    def test_literal_related(self):
        input_lines = """
            : test [ 42 ] literal ;
            test .
            bye
        """

        expected_output_lines = """
            : test [ 42 ] literal ;  ok
            test . 42  ok
            bye
        """

        self._run_script(input_lines, expected_output_lines)

    def test_immediate(self):
        input_lines = """
            : test1 cr 65 emit ; immediate
            : test2 test1 cr 66 emit ;
            test1
            test2
            bye
        """

        expected_output_lines = """
            : test1 cr 65 emit ; immediate  ok
            : test2 test1 cr 66 emit ;
            A ok
            test1
            A ok
            test2
            B ok
            bye
        """

        self._run_script(input_lines, expected_output_lines)

    def test_begin_again(self):
        input_lines = """
            : test cr begin key . again ;
            test
            abcde\003
            bye
        """

        expected_output_lines = """
            : test cr begin key . again ;  ok
            test
            97 98 99 100 101
            Use interrupt
              ok
            bye
        """

        self._run_script(input_lines, expected_output_lines)

    def test_postpone(self):
        "F.6.1.2033"
        input_lines = """
            : GT1 123 ;
            : GT4 POSTPONE GT1 ; IMMEDIATE
            : GT5 GT4 ;
            GT5 .
            : GT6 345 ; IMMEDIATE
            : GT7 POSTPONE GT6 ;
            GT7 .
            bye
        """

        expected_output_lines = """
            : GT1 123 ;  ok
            : GT4 POSTPONE GT1 ; IMMEDIATE  ok
            : GT5 GT4 ;  ok
            GT5 . 123  ok
            : GT6 345 ; IMMEDIATE  ok
            : GT7 POSTPONE GT6 ;  ok
            GT7 . 345  ok
            bye
        """

        self._run_script(input_lines, expected_output_lines)

    def test_paren(self):
        "F.6.1.0080"
        input_lines = """
            \\ There is no space either side of the ).
            ( A comment)1234 .
            : pc1 ( A comment)1234 ; pc1 .
        """

        expected_output_lines = """
            \\ There is no space either side of the ).  ok
            ( A comment)1234 . 1234  ok
            : pc1 ( A comment)1234 ; pc1 . 1234  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_create_body_does(self):
        "F.6.1.1250"
        input_lines = """
            : DOES1 DOES> @ 1 + ;
            : DOES2 DOES> @ 2 + ;
            CREATE CR1 .s
            CR1 here - .
            1 ,
            CR1 @ .
            DOES1 .S
            CR1 .
            DOES2 .S
            CR1 .
            : WEIRD: CREATE DOES> 1 + DOES> 2 + ; .S
            WEIRD: W1 .S
            ' W1 >BODY HERE - .
            W1 HERE 1 + - .
            W1 HERE 2 + - .
        """

        expected_output_lines = """
            : DOES1 DOES> @ 1 + ;  ok
            : DOES2 DOES> @ 2 + ;  ok
            CREATE CR1 .s <0>  ok
            CR1 here - . 0  ok
            1 ,  ok
            CR1 @ . 1  ok
            DOES1 .S <0>  ok
            CR1 . 2  ok
            DOES2 .S <0>  ok
            CR1 . 3  ok
            : WEIRD: CREATE DOES> 1 + DOES> 2 + ; .S <0>  ok
            WEIRD: W1 .S <0>  ok
            ' W1 >BODY HERE - . 0  ok
            W1 HERE 1 + - . 0  ok
            W1 HERE 2 + - . 0  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_variable(self):
        "F.6.1.2410"
        input_lines = """
            VARIABLE V1
            123 V1 !
            V1 @ .S
        """
        expected_output_lines = """
            VARIABLE V1  ok
            123 V1 !  ok
            V1 @ .S <1> 123  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_constant(self):
        "F.6.1.0950"
        input_lines = """
            123 CONSTANT X123
            X123 .
            : EQU CONSTANT ;
            X123 EQU Y123
            Y123 .
        """
        expected_output_lines = """
            123 CONSTANT X123  ok
            X123 . 123  ok
            : EQU CONSTANT ;  ok
            X123 EQU Y123  ok
            Y123 . 123  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_base(self):
        "F.6.1.0750"
        input_lines = """
            HEX
            : GN2 \\ ( -- 16 10 )
               BASE @ >R HEX BASE @ DECIMAL BASE @ R> BASE ! ;
            GN2 .S
        """
        expected_output_lines = """
            HEX  ok
            : GN2 \\ ( -- 16 10 )  ok
               BASE @ >R HEX BASE @ DECIMAL BASE @ R> BASE ! ;  ok
            GN2 .S <2> 10 A  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_tick(self):
        "F.6.1.0070"
        input_lines = """
            : GT1 123 ;
            ' GT1 EXECUTE .
        """
        expected_output_lines = """
            : GT1 123 ;  ok
            ' GT1 EXECUTE . 123  ok
        """

        self._run_script(input_lines, expected_output_lines)

    def test_bracket_tick(self):
        "F.6.1.2510"
        input_lines = """
            : GT1 123 ;
            : GT2 ['] GT1 ; IMMEDIATE
            GT2 EXECUTE .
        """
        expected_output_lines = """
            : GT1 123 ;  ok
            : GT2 ['] GT1 ; IMMEDIATE  ok
            GT2 EXECUTE . 123  ok
        """

        self._run_script(input_lines, expected_output_lines)


    def test_depth(self):
        "F.6.1.1200"
        input_lines = """
            0 1 DEPTH .S
            drop drop drop
              0 DEPTH .S
              drop drop
                DEPTH .S
        """
        expected_output_lines = """
            0 1 DEPTH .S <3> 0 1 2  ok
            drop drop drop  ok
              0 DEPTH .S <2> 0 1  ok
              drop drop  ok
                DEPTH .S <1> 0  ok
        """

        self._run_script(input_lines, expected_output_lines)


if __name__ == '__main__':
    unittest.main()
