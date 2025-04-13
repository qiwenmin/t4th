import os
import unittest
from unittest.mock import patch
from io import StringIO
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
            output = mock_stdout.getvalue().strip()

        if output:
            print(output)
            raise AssertionError('Test failed')
