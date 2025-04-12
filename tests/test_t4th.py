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

    def _run_scripts(self, scripts):
        input_lines = []
        expected_output_lines = []

        for script in textwrap.dedent(scripts).split('\n'):
            if not script.strip():
                continue
            input_line, expected_output_line = script.split(' ==>')
            inp = input_line.rstrip()
            if inp != '':
                input_lines.append(inp)
            expected_output_lines.append(expected_output_line[1:].rstrip())

        with patch('sys.stdin', new=StringIO('\n'.join(input_lines))), \
             patch('sys.stdout', new=StringIO()) as mock_stdout:
            t4th.main()
            output = mock_stdout.getvalue()
            output_lines = output.split('\n')
            welcome_line = output_lines[0]
            self._assert_welcome_message(welcome_line)

            output_lines = '\n'.join([s.rstrip() for s in output_lines[1:]]).rstrip()
            expected = '\n'.join(expected_output_lines).rstrip()

            self.assertEqual(output_lines, expected)

    def test_boot_and_bye(self):
        scripts = """
            bye ==>
        """
        self._run_scripts(scripts)

    def test_basic_stack_operations(self):
        scripts = """
            .S              ==> <0>  ok
            1 2 3           ==>  ok
            .S              ==> <3> 1 2 3  ok
            drop .S         ==> <2> 1 2  ok
            dup .S          ==> <3> 1 2 2  ok
            drop 4 swap .S  ==> <3> 1 4 2  ok
            over .S         ==> <4> 1 4 2 4  ok
        """

        self._run_scripts(scripts)

    def test_word_definition(self):
        scripts = """
            : square dup * ;        ==>  ok
            : cube dup square * ;   ==>  ok
            3 square . cr           ==> 9
                                    ==>  ok
            3 cube . cr             ==> 27
                                    ==>  ok
        """

        self._run_scripts(scripts)

    def test_literal_related(self):
        scripts = """
            : test [ 42 ] literal ; ==>  ok
            test . ==> 42  ok
        """

        self._run_scripts(scripts)

    def test_immediate(self):
        scripts = """
            : test1 cr 65 emit ; immediate  ==>  ok
            : test2 test1 cr 66 emit ;      ==>
                                            ==> A ok
            test1                           ==>
                                            ==> A ok
            test2                           ==>
                                            ==> B ok
        """

        self._run_scripts(scripts)

    def test_begin_again(self):
        scripts = """
            : test cr begin key . again ;   ==>  ok
            test                            ==>
            abcde\003                       ==> 97 98 99 100 101
                                            ==> Use interrupt
        """

        self._run_scripts(scripts)

    def test_forget(self):
        scripts = """
            here create foo create bar forget foo here - .  ==> 0  ok
            forget dup                                      ==>
                                                            ==> Error: Cannot forget `dup`
        """

        self._run_scripts(scripts)

    def test_input_tab_char(self):
        scripts = """
            123\t456\t.S ==> <2> 123 456  ok
        """
        self._run_scripts(scripts)

    def test_postpone(self):
        "F.6.1.2033"
        scripts = """
            : GT1 123 ;                     ==>  ok
            : GT4 POSTPONE GT1 ; IMMEDIATE  ==>  ok
            : GT5 GT4 ;                     ==>  ok
            GT5 .                           ==> 123  ok
            : GT6 345 ; IMMEDIATE           ==>  ok
            : GT7 POSTPONE GT6 ;            ==>  ok
            GT7 .                           ==> 345  ok
        """

        self._run_scripts(scripts)

    def test_paren(self):
        "F.6.1.0080"
        scripts = """
            \\ There is no space either side of the ).  ==>  ok
            ( A comment)1234 .                          ==> 1234  ok
            : pc1 ( A comment)1234 ; pc1 .              ==> 1234  ok
        """

        self._run_scripts(scripts)

    def test_create_body_does(self):
        "F.6.1.1250"
        scripts = """
            : DOES1 DOES> @ 1 + ;                       ==>  ok
            : DOES2 DOES> @ 2 + ;                       ==>  ok
            CREATE CR1 .s                               ==> <0>  ok
            CR1 here - .                                ==> 0  ok
            1 ,                                         ==>  ok
            CR1 @ .                                     ==> 1  ok
            DOES1 .S                                    ==> <0>  ok
            CR1 .                                       ==> 2  ok
            DOES2 .S                                    ==> <0>  ok
            CR1 .                                       ==> 3  ok
            : WEIRD: CREATE DOES> 1 + DOES> 2 + ; .S    ==> <0>  ok
            WEIRD: W1 .S                                ==> <0>  ok
            ' W1 >BODY HERE - .                         ==> 0  ok
            W1 HERE 1 + - .                             ==> 0  ok
            W1 HERE 2 + - .                             ==> 0  ok
        """

        self._run_scripts(scripts)

    def test_variable(self):
        "F.6.1.2410"
        scripts = """
            VARIABLE V1 ==>  ok
            123 V1 !    ==>  ok
            V1 @ .S     ==> <1> 123  ok
        """

        self._run_scripts(scripts)

    def test_constant(self):
        "F.6.1.0950"
        scripts = """
            123 CONSTANT X123   ==>  ok
            X123 .              ==> 123  ok
            : EQU CONSTANT ;    ==>  ok
            X123 EQU Y123       ==>  ok
            Y123 .              ==> 123  ok
        """

        self._run_scripts(scripts)

    def test_base(self):
        "F.6.1.0750"
        scripts = """
            HEX                                                 ==>  ok
            : GN2 \\ ( -- 16 10 )                               ==>  compiled
               BASE @ >R HEX BASE @ DECIMAL BASE @ R> BASE ! ;  ==>  ok
            GN2 .S                                              ==> <2> 10 A  ok
        """

        self._run_scripts(scripts)

    def test_tick(self):
        "F.6.1.0070"
        scripts = """
            : GT1 123 ;     ==>  ok
            ' GT1 EXECUTE . ==> 123  ok
        """

        self._run_scripts(scripts)

    def test_bracket_tick(self):
        "F.6.1.2510"
        scripts = """
            : GT1 123 ;                 ==>  ok
            : GT2 ['] GT1 ; IMMEDIATE   ==>  ok
            GT2 EXECUTE .               ==> 123  ok
        """

        self._run_scripts(scripts)


    def test_depth(self):
        "F.6.1.1200"
        scripts = """
            0 1 DEPTH .S    ==> <3> 0 1 2  ok
            drop drop drop  ==>  ok
              0 DEPTH .S    ==> <2> 0 1  ok
              drop drop     ==>  ok
                DEPTH .S    ==> <1> 0  ok
        """

        self._run_scripts(scripts)

    def test_if_then_else(self):
        "F.6.1.1700"
        scripts = """
            : GI1 IF 123 THEN ;                             ==>  ok
            : GI2 IF 123 ELSE 234 THEN ;                    ==>  ok
             0 GI1 .S                                       ==> <0>  ok
             1 GI1 .                                        ==> 123  ok
            -1 GI1 .                                        ==> 123  ok
             0 GI2 .                                        ==> 234  ok
             1 GI2 .                                        ==> 123  ok
            -1 GI1 .                                        ==> 123  ok
            \\ Multiple ELSEs in an IF statement            ==>  ok
            : melse IF 1 ELSE 2 ELSE 3 ELSE 4 ELSE 5 THEN ; ==>  ok
            <FALSE> melse . .                               ==> 4 2  ok
            <TRUE>  melse . . .                             ==> 5 3 1  ok
        """

        self._run_scripts(scripts)

    def test_state(self):
        "F.6.1.2250"
        scripts = """
            : GT8 STATE @ ; IMMEDIATE ==>  ok
            GT8 .                     ==> 0  ok
            : GT9 GT8 LITERAL ;       ==>  ok
            GT9 0= <FALSE> - .        ==> 0  ok
        """

        self._run_scripts(scripts)

    def test_char(self):
        "F.6.1.0895"
        scripts = """
            HEX          ==>  ok
            CHAR X .     ==> 58  ok
            CHAR HELLO . ==> 48  ok
        """

        self._run_scripts(scripts)

    def test_bracket_char(self):
        "F.6.1.2520"
        scripts = """
            HEX                     ==>  ok
            : GC1 [CHAR] X     ;    ==>  ok
            : GC2 [CHAR] HELLO ;    ==>  ok
            GC1 .                   ==> 58  ok
            GC2 .                   ==> 48  ok
        """

        self._run_scripts(scripts)


if __name__ == '__main__':
    unittest.main()
