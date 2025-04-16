import os
import unittest
from unittest.mock import patch
from io import StringIO
import textwrap
from t4th import t4th

class TestStandard(unittest.TestCase):

    def setUp(self):
        self.t4th = t4th.T4th()
        self.t4th._load_core_fs()
        current_dir = os.path.dirname(__file__)
        self.t4th.load_and_run_file(os.path.join(current_dir, 'ttester.fs'))

    def test_core(self):
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            current_dir = os.path.dirname(__file__)
            self.t4th.load_and_run_file(os.path.join(current_dir, 'test_core.fs'))
            output = mock_stdout.getvalue().lstrip()

        expected_output = textwrap.dedent("""\
            You should see 2345: 2345
            YOU SHOULD SEE THE STANDARD GRAPHIC CHARACTERS:
             !"#$%&'()*+,-./0123456789:;<=>?@
            ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`
            abcdefghijklmnopqrstuvwxyz{|}~
            YOU SHOULD SEE 0-9 SEPARATED BY A SPACE:
            0 1 2 3 4 5 6 7 8 9 \n\
            YOU SHOULD SEE 0-9 (WITH NO SPACES):
            0123456789
            YOU SHOULD SEE A-G SEPARATED BY A SPACE:
            A B C D E F G \n\
            YOU SHOULD SEE 0-5 SEPARATED BY TWO SPACES:
            0  1  2  3  4  5  \n\
            YOU SHOULD SEE TWO SEPARATE LINES:
            LINE 1
            LINE 2
            YOU SHOULD SEE THE NUMBER RANGES OF SIGNED AND UNSIGNED NUMBERS:
            SIGNED: -80000000 7FFFFFFF \n\
            UNSIGNED: 0 FFFFFFFF \n\
        """)

        self.assertEqual(output, expected_output)
