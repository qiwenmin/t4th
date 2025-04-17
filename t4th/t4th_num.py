from ctypes import c_int32, c_uint32, c_int64, c_uint64, sizeof

base = lambda : 10

int_type = c_int32
uint_type = c_uint32
dint_type = c_int64
duint_type = c_uint64

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

def i2u(n: int):
    return uint_type(n).value

def i2d(n: int):
    d = dint_type(n).value
    return (d & int_mask, d >> int_bits)

class I(int_type):
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
        return I((self.value & int_mask) >> n)

    def lshift(self, n):
        return I(((self.value & int_mask) << n) & int_mask)

    def um_mod(self, ud1, ud2):
        u1 = uint_type(self.value).value & int_mask
        ud1 = uint_type(ud1).value & int_mask
        ud2 = uint_type(ud2).value & int_mask

        ud = ud1 + (ud2 << int_bits)

        q = ud // u1
        r = ud % u1
        return (I(r), I(q))

    def um_star(self, u):
        u1 = uint_type(self.value).value & int_mask
        u2 = uint_type(u).value & int_mask

        ud = u1 * u2
        ud1 = ud & int_mask
        ud2 = (ud >> int_bits) & int_mask

        return (I(ud1), I(ud2))

    def fm_mod(self, d1, d2):
        n1 = int_type(self.value).value
        d1 = uint_type(d1).value
        d2 = uint_type(d2).value

        d = dint_type(d1 + (d2 << int_bits)).value

        q = d // n1
        r = d % n1
        return (I(r), I(q))

    def sm_rem(self, d1, d2):
        n1 = int_type(self.value).value
        d1 = int_type(d1).value
        d2 = int_type(d2).value

        d = dint_type((d1 & int_mask) + (d2 << int_bits)).value

        q = int(d / n1)
        r = d - q * n1

        return (I(r), I(q))

    def m_star(self, n):
        n1 = int_type(self.value).value
        n2 = int_type(n).value

        d = n1 * n2

        d1 = d & int_mask
        d2 = (d >> int_bits) & int_mask

        return (I(d1), I(d2))

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
