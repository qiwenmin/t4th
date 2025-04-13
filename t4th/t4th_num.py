from ctypes import c_int, c_uint, sizeof

base = lambda : 10

int_type = c_int
uint_type = c_uint

int_bits = sizeof(int_type) * 8
int_mask = (1 << int_bits) - 1

def int_to_base(n: int) -> str:
    if not (2 <= base() <= 36):
        raise ValueError("Base must be between 2 and 36")
    if n == 0:
        return '0'

    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    is_negative = n < 0
    n = abs(n)
    res = ""
    while n:
        res = digits[n % base()] + res
        n //= base()
    return '-' + res if is_negative else res

class I(c_int):
    def __repr__(self):
        return f'{int_to_base(self.value)}'

    def __add__(self, other):
        return I((self.value & int_mask) + (_v_in(other).value & int_mask))

    def __sub__(self, other):
        return I((self.value & int_mask) - (_v_in(other).value & int_mask))

    def __mul__(self, other):
        return I((self.value & int_mask) * (_v_in(other).value & int_mask))

    def invert(self):
        return I(~self.value & int_mask)

    def rshift(self, n):
        return I(self.value & int_mask >> n)

    def um_mod(self, ud1, ud2):
        u1 = uint_type(self.value).value & int_mask
        ud1 = uint_type(ud1).value & int_mask
        ud2 = uint_type(ud2).value & int_mask

        ud = ud1 + (ud2 << int_bits)

        q = ud // u1
        r = ud % u1
        return (I(r), I(q))



def _v_in(v):
    if isinstance(v, I):
        return v
    elif isinstance(v, int):
        return I(v)
    else:
        return v

def _v_out(v):
    if isinstance(v, I):
        return v.value
    else:
        return v

class memory(list):
    def __init__(self, size=0):
        if size != 0:
            super().__init__([I(0)] * size)
        else:
            super().__init__()
    def append(self, v):
        super().append(_v_in(v))
    def __setitem__(self, i, v):
        super().__setitem__(i, _v_in(v))
    def __getitem__(self, i):
        return _v_out(super().__getitem__(i))
    def __iter__(self):
        return (_v_out(x) for x in super().__iter__())
    def pop(self):
        return _v_out(super().pop())

