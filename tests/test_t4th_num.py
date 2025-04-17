import unittest
import t4th.t4th_num as t4n

class TestT4thNum(unittest.TestCase):
    def test_int_to_base_fail(self):
        t4n.base = lambda : 37
        with self.assertRaises(ValueError):
            t4n.int_to_base(123)

    def test_i_repr(self):
        i = t4n.I(42)
        t4n.base = lambda :10
        self.assertEqual(f'{i}', '42')
        t4n.base = lambda :16
        self.assertEqual(f'{i}', '2A')

    def test_ch_to_int_fail(self):
        t4n.base = lambda : 37
        with self.assertRaises(ValueError):
            t4n.ch_to_int('0')
