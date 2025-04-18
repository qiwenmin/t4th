#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import StringIO
import os
import sys
import t4th.t4th_num as tn
from ctypes import c_int
from typing import Optional
from enum import Enum, auto
from .input import get_raw_input, get_input_line

class T4th:
    _version = '0.1.0'

    class MemAddress(Enum):
        SOURCE_N = 0
        IN_BUFFER_ADDR = auto()
        IN_BUFFER_LEN = 256 - 1

        PAD_BUFFER = IN_BUFFER_ADDR + IN_BUFFER_LEN
        PAD_BUFFER_LEN = 256

        PAD_END = PAD_BUFFER + PAD_BUFFER_LEN - 1
        EXEC_START = PAD_BUFFER + PAD_BUFFER_LEN

        DP = auto()
        BASE = auto()
        STATE = auto()
        SOURCE_P = auto()
        TO_IN = auto()

        END = auto()

    class _Word:
        FLAG_IMMEDIATE = 1 << 0
        FLAG_NON_INTERACTIVE = 1 << 1

        def __init__(self, word_name:str, ptr:int=0, flag=0, prev:int=0):
            self.word_name = word_name.upper()
            self.ptr = ptr
            self.flag = flag
            self.prev = prev

        def __str__(self):
            return f"`{self.word_name}`{'I' if self.is_immediate() else ''}/{self.prev}"

        def __repr__(self):
            return self.__str__()

        def is_immediate(self):
            return (self.flag & T4th._Word.FLAG_IMMEDIATE) != 0

        def is_non_interactive(self):
            return (self.flag & T4th._Word.FLAG_NON_INTERACTIVE)!= 0

    class _PrimitiveWord:
        def __init__(self, name:str, ptr:int):
            self.name = name.upper()
            self.ptr = ptr

        def __call__(self, *args):
            self.ptr(*args)

        def __str__(self):
            return f"`{self.name}`"

        def __repr__(self):
            return self.__str__()

    def _add_word(self, word:_Word):
        word.prev = self._latest_word_ptr
        self._latest_word_ptr = self._here()
        self._memory_append(word)

    def _find_word_ptr(self, word_name:str) -> int:
        word_name = word_name.upper()
        p = self._latest_word_ptr
        if self._get_var_value('STATE') != 0:
            p = self._memory[p].prev

        while p > 0 and self._memory[p].word_name!= word_name:
            p = self._memory[p].prev
        return p

    def _find_word_or_none(self, word_name:str) -> Optional[_Word]:
        p = self._find_word_ptr(word_name)
        if p == 0:
            return None
        return self._memory[p]

    def _find_word(self, word_name:str) -> _Word:
        word = self._find_word_or_none(word_name)
        if word is None:
            raise ValueError(f"Undefined word: `{word_name}`")
        return word

    def _VAR_WORD(self, name:str, alias:str=None) -> _Word:
        addr = T4th.MemAddress[name].value
        return (T4th._Word(alias if alias else name), lambda: self._data_stack.append(addr))

    def _set_var_value(self, name:str, value:int):
        addr = T4th.MemAddress[name].value
        self._memory[addr] = value

    def _inc_var(self, name:str, i:int=1):
        addr = T4th.MemAddress[name].value
        self._memory[addr] += i

    def _get_var_value(self, name:str) -> int:
        addr = T4th.MemAddress[name].value
        return self._memory[addr]

    def __init__(self, memory_size=65536):
        tn.base = lambda : self._base()

        self._memory_size = memory_size

        IM = T4th._Word.FLAG_IMMEDIATE
        NI = T4th._Word.FLAG_NON_INTERACTIVE

        self._primitive_words = [
            (T4th._Word('.VM'), self._word_dot_vm),

            (T4th._Word('BYE'), self._word_bye),
            (T4th._Word('ABORT'), self._word_abort),
            (T4th._Word('EVALUATE'), self._word_evaluate),

            self._VAR_WORD('DP'),
            self._VAR_WORD('BASE'),
            self._VAR_WORD('STATE'),
            self._VAR_WORD('TO_IN', '>IN'),
            self._VAR_WORD('PAD_BUFFER', 'PAD'),
            self._VAR_WORD('PAD_END', 'PAD-END'),

            (T4th._Word('ENVIRONMENT?'), self._word_environment_query),

            (T4th._Word('WORDS'), self._word_words),
            (T4th._Word('FORGET'), self._word_forget),

            (T4th._Word('(', flag=IM), self._word_paren),

            (T4th._Word('.S'), self._word_dot_s),
            (T4th._Word('.'), self._word_dot),
            (T4th._Word('U.'), self._word_u_dot),
            (T4th._Word('EMIT'), self._word_emit),
            (T4th._Word('CR'), self._word_cr),

            (T4th._Word('DEPTH'), self._word_depth),
            (T4th._Word('DUP'), self._word_dup),
            (T4th._Word('DROP'), self._word_drop),
            (T4th._Word('SWAP'), self._word_swap),
            (T4th._Word('OVER'), self._word_over),
            (T4th._Word('PICK'), self._word_pick),

            (T4th._Word('!'), self._word_mem_store),
            (T4th._Word('@'), self._word_mem_fetch),
            (T4th._Word(','), self._word_comma),

            (T4th._Word('MOVE'), self._word_move),

            (T4th._Word('>R'), self._word_to_r),
            (T4th._Word('R>'), self._word_r_from),
            (T4th._Word('R@'), self._word_r_fetch),

            (T4th._Word('+'), self._word_add),
            (T4th._Word('-'), self._word_sub),
            (T4th._Word('*'), self._word_mul),
            (T4th._Word('/'), self._word_div),
            (T4th._Word('MOD'), self._word_mod),
            (T4th._Word('/MOD'), self._word_slash_mod),

            (T4th._Word('M*'), self._word_m_star),

            (T4th._Word('UM*'), self._word_um_star),
            (T4th._Word('UM/MOD'), self._word_um_slash_mod),

            (T4th._Word('FM/MOD'), self._word_fm_slash_mod),
            (T4th._Word('*/MOD'), self._word_star_slash_mod),

            (T4th._Word('SM/REM'), self._word_sm_slash_rem),

            (T4th._Word('INVERT'), self._word_invert),
            (T4th._Word('AND'), self._word_and),
            (T4th._Word('OR'), self._word_or),
            (T4th._Word('XOR'), self._word_xor),
            (T4th._Word('RSHIFT'), self._word_rshift),
            (T4th._Word('LSHIFT'), self._word_lshift),

            (T4th._Word('<'), self._word_less),
            (T4th._Word('0='), self._word_zero_equ),
            (T4th._Word('0<'), self._word_zero_less),

            (T4th._Word('U<'), self._word_u_less),

            (T4th._Word('COMPARE'), self._word_compare),

            (T4th._Word('DOCOL', flag=NI), self._word_docol),
            (T4th._Word(':'), self._word_define),
            (T4th._Word(':NONAME'), self._word_colon_noname),
            (T4th._Word(';', flag=IM), self._word_end_def),
            (T4th._Word('EXIT', flag=NI), self._word_exit),
            (T4th._Word('RECURSE', flag=IM|NI), self._word_recurse),

            (T4th._Word('IMMEDIATE'), self._word_immediate),

            (T4th._Word('POSTPONE', flag=IM|NI), self._word_postpone),
            (T4th._Word('[COMPILE]', flag=IM|NI), self._word_bracket_compile),
            (T4th._Word('COMPILE,'), self._word_compile_comma),

            (T4th._Word('(CREATE)', flag=NI), self._word_create_p),
            (T4th._Word('CREATE'), self._word_create),
            (T4th._Word('DOES>', flag=NI), self._word_does),

            (T4th._Word('LITERAL', flag=IM|NI), self._word_literal),
            (T4th._Word('(LITERAL)', flag=NI), self._word_literal_p),

            (T4th._Word('CHAR'), self._word_char),

            (T4th._Word(']'), self._word_right_bracket),
            (T4th._Word('[', flag=IM|NI), self._word_left_bracket),

            (T4th._Word('\''), self._word_tick),
            (T4th._Word('EXECUTE'), self._word_execute),
            (T4th._Word('FIND'), self._word_find),

            (T4th._Word('BRANCH', flag=NI), self._word_branch),
            (T4th._Word('0BRANCH', flag=NI), self._word_0branch),

            (T4th._Word('[ELSE]', flag=IM), self._word_bracket_else),

            (T4th._Word('DO', flag=IM|NI), self._word_do),
            (T4th._Word('?DO', flag=IM|NI), self._word_question_do),
            (T4th._Word('LOOP', flag=IM|NI), self._word_loop),
            (T4th._Word('+LOOP', flag=IM|NI), self._word_plus_loop),
            (T4th._Word('LEAVE', flag=NI), self._word_leave),
            (T4th._Word('UNLOOP', flag=NI), self._word_unloop),
            (T4th._Word('I', flag=NI), self._word_i),
            (T4th._Word('J', flag=NI), self._word_j),
            (T4th._Word('K', flag=NI), self._word_k),

            (T4th._Word('KEY'), self._word_key),

            (T4th._Word('ACCEPT'), self._word_accept),
            (T4th._Word('REFILL'), self._word_refill),
            (T4th._Word('PARSE'), self._word_parse),
            (T4th._Word('WORD'), self._word_word),
            (T4th._Word('TYPE'), self._word_type),

            (T4th._Word('>NUMBER'), self._word_to_number),

            (T4th._Word('SOURCE'), self._word_source),
            (T4th._Word('SAVE-INPUT'), self._word_save_input),
            (T4th._Word('RESTORE-INPUT'), self._word_restore_input),

            (T4th._Word('INCLUDED'), self._word_included),
        ]

        self._init_vm()

    # primitive words implementation

    def _word_dot_vm(self):
        print()
        print(f'Memory: {self._memory[:self._memory[T4th.MemAddress.DP.value]]}')

        print(f' STACK: {self._data_stack}')
        print(f'     R: {self._return_stack}')
        print(f'    PC: {self._pc}')
        print(f' STATE: {self._get_var_value('STATE')}')
        print(f'  BASE: {self._base()}')
        print(f'LATEST: {self._latest_word_ptr}')

    def _word_bye(self):
        print()
        self._quit = True

    def _word_abort(self):
        raise RuntimeError('Aborted')

    def _word_evaluate(self):
        self._check_stack(2)
        u = self._data_stack.pop()
        c_addr = self._data_stack.pop()

        # 备份状态
        pc = self._pc
        input_backup = self._input_backup()

        # 准备好evaluate的环境
        self._in_stream = StringIO('')
        self._source_addr_set(c_addr)
        self._source_n_set(u)
        self._to_in_set(0)

        self._prompt = ''
        self._evaluating = True

        # 执行
        self.interpret()

        # 还原状态
        self._evaluating = False
        self._prompt = ''

        self._input_restore(input_backup)
        self._pc = pc

    def _word_environment_query(self):
        self._check_stack(2)
        u = self._data_stack.pop()
        c_addr = self._data_stack.pop()

        env_name = self._copy_counted_str(c_addr, u)
        if env_name == 'X:deferred':
            self._data_stack.append(-1)
        else:
            self._data_stack.append(0)

    def _word_words(self):
        print()
        p = self._latest_word_ptr
        while p > 0:
            print(self._memory[p].word_name, end=' ')
            p = self._memory[p].prev

    def _word_forget(self):
        p_begin = self._find_word_ptr('USER-WORD-BEGIN')
        word_name = self._get_next_word()
        p = self._find_word_ptr(word_name)
        if p > p_begin:
            self._forget_p(p)
        else:
            raise ValueError(f'Cannot forget `{word_name}`')

    def _word_paren(self):
        if not self._get_until_char(')'):
            raise ValueError('Unclosed parenthesis')

    def _word_dot_s(self):
        print(f'<{len(self._data_stack)}> ', end='', flush=True)
        for v in self._data_stack:
            print(f'{tn.int_to_base(v)}', end=' ', flush=True)

    def _word_dot(self):
        self._check_stack(1)
        print(f'{tn.int_to_base(self._data_stack.pop())} ', end='', flush=True)

    def _word_u_dot(self):
        self._check_stack(1)
        print(f'{tn.int_to_base(tn.i2u(self._data_stack.pop()))} ', end='', flush=True)

    def _word_emit(self):
        self._check_stack(1)
        print(chr(self._data_stack.pop()), end='', flush=True)

    def _word_cr(self):
        print()

    def _word_depth(self):
        self._data_stack.append(len(self._data_stack))

    def _word_dup(self):
        self._check_stack(1)

        self._data_stack.append(self._data_stack[-1])

    def _word_drop(self):
        self._check_stack(1)

        self._data_stack.pop()

    def _word_swap(self):
        self._check_stack(2)

        a = self._data_stack.pop()
        b = self._data_stack.pop()
        self._data_stack.append(a)
        self._data_stack.append(b)

    def _word_over(self):
        self._check_stack(2)

        self._data_stack.append(self._data_stack[-2])

    def _word_pick(self):
        self._check_stack(1)
        n = self._data_stack.pop()
        self._check_stack(n + 1)

        self._data_stack.append(self._data_stack[-n-1])

    def _word_mem_store(self):
        self._check_stack(2)

        addr = self._data_stack.pop()
        x = self._data_stack.pop()
        self._memory[addr] = x

    def _word_mem_fetch(self):
        self._check_stack(1)

        addr = self._data_stack.pop()
        x = self._memory[addr]
        self._data_stack.append(x)

    def _word_comma(self):
        self._check_stack(1)

        self._memory_append(self._data_stack.pop())

    def _word_move(self):
        self._check_stack(3)
        u = self._data_stack.pop()
        addr2 = self._data_stack.pop()
        addr1 = self._data_stack.pop()

        if addr1 >= addr2:
            for i in range(u):
                self._memory[addr2 + i] = self._memory[addr1 + i]
        else:
            # 要防止覆盖，从后向前复制
            for i in range(u-1, -1, -1):
                self._memory[addr2 + i] = self._memory[addr1 + i]

    def _word_to_r(self):
        self._check_stack(1)

        self._return_stack.append(self._data_stack.pop())

    def _word_r_from(self):
        self._check_return_stack(1)

        self._data_stack.append(self._return_stack.pop())

    def _word_r_fetch(self):
        self._check_return_stack(1)

        self._data_stack.append(self._return_stack[-1])

    def _word_add(self):
        self._check_stack(2)

        self._data_stack.append(tn.I(self._data_stack.pop()) + tn.I(self._data_stack.pop()))

    def _word_sub(self):
        self._check_stack(2)

        self._data_stack.append(tn.I(-self._data_stack.pop()) - tn.I(-self._data_stack.pop()))

    def _word_mul(self):
        self._check_stack(2)

        self._data_stack.append(tn.I(self._data_stack.pop()) * tn.I(self._data_stack.pop()))

    def _word_div(self):
        self._check_stack(2)

        a = self._data_stack.pop()
        b = self._data_stack.pop()
        if a == 0:
            raise ValueError('Division by zero')

        self._data_stack.append(b // a)

    def _word_mod(self):
        self._check_stack(2)

        n2 = self._data_stack.pop()
        n1 = self._data_stack.pop()
        if n2 == 0:
            raise ValueError('Division by zero')

        self._data_stack.append(n1 % n2)

    def _word_slash_mod(self):
        self._check_stack(2)

        n2 = self._data_stack.pop()
        n1 = self._data_stack.pop()

        if n2 == 0:
            raise ValueError('Division by zero')

        self._data_stack.append(n1 % n2)
        self._data_stack.append(n1 // n2)

    def _word_m_star(self):
        self._check_stack(2)

        n2 = self._data_stack.pop()
        n1 = self._data_stack.pop()

        (d1, d2) = tn.I(n2).m_star(n1)
        self._data_stack.append(d1)
        self._data_stack.append(d2)

    def _word_um_star(self):
        self._check_stack(2)
        u2 = self._data_stack.pop()
        u1 = self._data_stack.pop()

        (ud1, ud2) = tn.I(u1).um_star(u2)

        self._data_stack.append(ud1)
        self._data_stack.append(ud2)

    def _word_um_slash_mod(self):
        self._check_stack(3)
        u1 = self._data_stack.pop()
        ud2 = self._data_stack.pop()
        ud1 = self._data_stack.pop()

        if u1 == 0:
            raise ValueError('Division by zero')

        (r, q) = tn.I(u1).um_mod(ud1, ud2)

        self._data_stack.append(r)
        self._data_stack.append(q)

    def _word_fm_slash_mod(self):
        self._check_stack(3)
        n1 = self._data_stack.pop()
        d2 = self._data_stack.pop()
        d1 = self._data_stack.pop()

        if n1 == 0:
            raise ValueError('Division by zero')

        (r, q) = tn.I(n1).fm_mod(d1, d2)

        self._data_stack.append(r)
        self._data_stack.append(q)

    def _word_star_slash_mod(self):
        self._check_stack(3)
        n3 = self._data_stack.pop()
        n2 = self._data_stack.pop()
        n1 = self._data_stack.pop()

        if n3 == 0:
            raise ValueError('Division by zero')

        d = n1 * n2
        n4 = d % n3
        n5 = d // n3

        self._data_stack.append(n4)
        self._data_stack.append(n5)

    def _word_sm_slash_rem(self):
        self._check_stack(3)
        n1 = self._data_stack.pop()
        d2 = self._data_stack.pop()
        d1 = self._data_stack.pop()

        if n1 == 0:
            raise ValueError('Division by zero')

        (r, q) = tn.I(n1).sm_rem(d1, d2)

        self._data_stack.append(r)
        self._data_stack.append(q)

    def _word_invert(self):
        self._check_stack(1)
        self._data_stack.append(tn.I(self._data_stack.pop()).invert())

    def _word_and(self):
        self._check_stack(2)
        self._data_stack.append(self._data_stack.pop() & self._data_stack.pop())

    def _word_or(self):
        self._check_stack(2)
        self._data_stack.append(self._data_stack.pop() | self._data_stack.pop())

    def _word_xor(self):
        self._check_stack(2)
        self._data_stack.append(self._data_stack.pop() ^ self._data_stack.pop())

    def _word_rshift(self):
        self._check_stack(2)
        shift = self._data_stack.pop()
        self._data_stack.append(tn.I(self._data_stack.pop()).rshift(shift))

    def _word_lshift(self):
        self._check_stack(2)
        shift = self._data_stack.pop()
        self._data_stack.append(tn.I(self._data_stack.pop()).lshift(shift))

    def _word_less(self):
        self._check_stack(2)
        self._data_stack.append(-1 if self._data_stack.pop() > self._data_stack.pop() else 0)

    def _word_zero_equ(self):
        self._check_stack(1)
        self._data_stack.append(-1 if self._data_stack.pop() == 0 else 0)

    def _word_zero_less(self):
        self._check_stack(1)
        self._data_stack.append(-1 if self._data_stack.pop() < 0 else 0)

    def _word_u_less(self):
        self._check_stack(2)
        self._data_stack.append(-1 if tn.i2u(self._data_stack.pop()) > tn.i2u(self._data_stack.pop()) else 0)

    def _word_compare(self):
        self._check_stack(4)

        u2 = self._data_stack.pop()
        addr2 = self._data_stack.pop()
        u1 = self._data_stack.pop()
        addr1 = self._data_stack.pop()

        for i in range(min(u1, u2)):
            if self._memory[addr1 + i] < self._memory[addr2 + i]:
                self._data_stack.append(-1)
                return
            elif self._memory[addr1 + i] > self._memory[addr2 + i]:
                self._data_stack.append(1)
                return

        if u1 < u2:
            self._data_stack.append(-1)
        elif u1 > u2:
            self._data_stack.append(1)
        else:
            self._data_stack.append(0)

    def _word_docol(self):
        self._return_stack.append(self._pc)
        self._pc = self._exec_pc + 1

    def _word_define(self):
        word_name = self._get_next_word()

        docol = self._find_word('DOCOL')
        w = T4th._Word(word_name, self._here() + 1, prev=self._latest_word_ptr)
        self._add_word(w)
        self._memory_append(self._memory[docol.ptr])

        self._return_stack.append(w.ptr)

        self._set_var_value('STATE', -1)

    def _word_colon_noname(self):
        docol = self._find_word('DOCOL')
        w = T4th._Word(" noname", self._here() + 1, prev=self._latest_word_ptr) # " noname"包含空格，不可能被parse出来的word_name匹配上。
        self._add_word(w)
        self._memory_append(self._memory[docol.ptr])
        self._data_stack.append(w.ptr)
        self._return_stack.append(w.ptr)
        self._set_var_value('STATE', -1)

    def _word_end_def(self):
        self._check_return_stack(1)
        self._return_stack.pop()

        self._memory_append(self._find_word('EXIT').ptr)
        self._set_var_value('STATE', 0)

    def _word_exit(self):
        self._check_return_stack(1)

        self._pc = self._return_stack.pop()

    def _word_recurse(self):
        self._check_return_stack(1)

        self._memory_append(self._return_stack[-1])

    def _word_immediate(self):
        if self._latest_word_ptr > 0:
            self._memory[self._latest_word_ptr].flag |= T4th._Word.FLAG_IMMEDIATE

    def _word_postpone(self):
        word_name = self._get_next_word()
        w = self._find_word(word_name)
        if w.is_immediate():
            self._memory_append(w.ptr)
        else:
            self._memory_append(self._find_word('(LITERAL)').ptr)
            self._memory_append(w.ptr)
            self._memory_append(self._find_word(',').ptr)

    def _word_bracket_compile(self):
        word_name = self._get_next_word()
        w = self._find_word(word_name)
        self._memory_append(w.ptr)

    def _word_compile_comma(self):
        self._check_stack(1)
        self._memory_append(self._data_stack.pop())

    def _word_create_p(self):
        self._data_stack.append(self._exec_pc + 1)

    def _word_create(self):
        word_name = self._get_next_word()

        create_p = self._find_word('(CREATE)')
        w = T4th._Word(word_name, self._here() + 1, prev=self._latest_word_ptr)
        self._add_word(w)
        self._memory_append(self._memory[create_p.ptr])

    def _new_does_p(self, jmp_ptr):
        def does_p():
            self._data_stack.append(self._exec_pc + 1)

            self._return_stack.append(self._pc)
            self._pc = jmp_ptr

        return does_p

    def _word_does(self):
        jmp_ptr = self._pc
        does_p = T4th._PrimitiveWord('(DOES>)', self._new_does_p(jmp_ptr))
        this_word = self._memory[self._latest_word_ptr]
        self._memory[this_word.ptr] = does_p

        self._word_exit()

    def _word_literal(self):
        self._check_stack(1)

        w = self._find_word('(LITERAL)')
        self._memory_append(w.ptr)
        self._memory_append(self._data_stack.pop())

    def _word_literal_p(self):
        value = self._memory[self._pc]
        self._data_stack.append(value)
        self._pc += 1

    def _word_char(self):
        word_name = self._get_next_word()
        ch = word_name[0]
        self._data_stack.append(ord(ch))

    def _word_right_bracket(self):
        self._set_var_value('STATE', -1)

    def _word_left_bracket(self):
        self._set_var_value('STATE', 0)

    def _word_tick(self):
        word_name = self._get_next_word()
        w = self._find_word(word_name)
        self._data_stack.append(w.ptr)

    def _word_execute(self):
        self._check_stack(1)

        xt = self._data_stack.pop()
        self._exec_pc = xt
        self._memory[xt]()

    def _word_find(self):
        self._check_stack(1)
        c_addr = self._data_stack.pop()
        word_name = self._copy_counted_str(c_addr)

        w = self._find_word_or_none(word_name)
        if w is None:
            self._data_stack.append(c_addr)
            self._data_stack.append(0)
        else:
            self._data_stack.append(w.ptr)
            self._data_stack.append(1 if w.is_immediate() else -1)

    def _word_branch(self):
        self._pc = self._memory[self._pc]

    def _word_0branch(self):
        self._check_stack(1)

        if self._data_stack.pop() == 0:
            self._pc = self._memory[self._pc]
        else:
            self._pc += 1

    def _word_bracket_else(self):
        level = 1
        while True:
            next_word = self._get_next_word_or_none()
            if next_word is None:
                raise ValueError('Unclosed [ELSE]')

            next_word = next_word.upper()
            if next_word == '[IF]':
                level += 1
            elif next_word == '[ELSE]':
                level -= 1
                if level != 0:
                    level += 1
            elif next_word == '[THEN]':
                level -= 1

            if level == 0:
                break

    def _word_do(self):
        """
        编译后：
        +----+------------+-----+
        | DO | leave_addr | ... |
        +----+-----+------+-----+
                   |           ^
                   |           |
        +-------+  |           +-----+
        | LEAVE |  +---------+       |
        +-------+            |       |
                             V       |
        +------+-----------+-----+   |
        | LOOP | loop_addr | ... |   |
        +------+-----+-----+-----+   |
                     |               |
                     +---------------+

        运行时的返回栈：
        ( R: leave_addr limit index )
        """
        if self._get_var_value('STATE') != 0:
            # 定义中
            self._memory_append(self._find_word('DO').ptr)
            self._data_stack.append(self._here()) # 需要loop在编译时回填的leave_addr的位置
            self._memory_append(0) # 填0占位
        else:
            # 运行时
            index = self._data_stack.pop()
            limit = self._data_stack.pop()

            self._return_stack.append(self._memory[self._pc])
            self._return_stack.append(limit)
            self._return_stack.append(index)
            self._pc += 1

    def _word_question_do(self):
        if self._get_var_value('STATE') != 0:
            # 定义中
            self._memory_append(self._find_word('?DO').ptr)
            self._data_stack.append(self._here()) # 需要loop在编译时回填的leave_addr的位置
            self._memory_append(0) # 填0占位
        else:
            # 运行时
            index = self._data_stack.pop()
            limit = self._data_stack.pop()
            leave_addr = self._memory[self._pc]

            if limit != index:
                self._return_stack.append(leave_addr)
                self._return_stack.append(limit)
                self._return_stack.append(index)
                self._pc += 1
            else:
                self._pc = leave_addr

    def _word_loop(self):
        if self._get_var_value('STATE') != 0:
            # 定义中
            self._check_stack(1)
            self._memory_append(self._find_word('LOOP').ptr)
            leave_fill_addr = self._data_stack.pop()
            self._memory_append(leave_fill_addr + 1)
            self._memory[leave_fill_addr] = self._here()
        else:
            # 运行时
            self._check_return_stack(3)
            index = self._return_stack[-1]
            limit = self._return_stack[-2]

            index += 1
            index = tn.I(index).value

            if index < limit:
                self._return_stack[-1] = index
                self._pc = self._memory[self._pc]
            else:
                self._return_stack.pop()
                self._return_stack.pop()
                self._return_stack.pop()
                self._pc += 1

    def _word_plus_loop(self):
        if self._get_var_value('STATE') != 0:
            # 定义中
            self._check_stack(1)
            self._memory_append(self._find_word('+LOOP').ptr)
            leave_fill_addr = self._data_stack.pop()
            self._memory_append(leave_fill_addr + 1)
            self._memory[leave_fill_addr] = self._here()
        else:
            # 运行时
            self._check_return_stack(3)
            index = self._return_stack[-1]
            limit = self._return_stack[-2]

            self._check_stack(1)

            step = self._data_stack.pop()
            old_index = index
            index += step
            index = tn.I(index).value

            if not (
                (step > 0 and
                    (tn.I(limit) - tn.I(old_index)).value > 0 and
                    (tn.I(index) - tn.I(limit)).value >= 0)
                or
                (step < 0 and
                    (tn.I(limit) - tn.I(old_index)).value <= 0 and
                    (tn.I(index) - tn.I(limit)).value < 0)):
                self._return_stack[-1] = index
                self._pc = self._memory[self._pc]
            else:
                self._return_stack.pop()
                self._return_stack.pop()
                self._return_stack.pop()
                self._pc += 1

    def _word_leave(self):
        self._check_return_stack(3)
        self._return_stack.pop()
        self._return_stack.pop()
        leave_addr = self._return_stack.pop()
        self._pc = leave_addr

    def _word_unloop(self):
        self._check_return_stack(3)
        self._return_stack.pop()
        self._return_stack.pop()
        self._return_stack.pop()

    def _word_i(self):
        self._check_return_stack(3)
        self._data_stack.append(self._return_stack[-1])

    def _word_j(self):
        self._check_return_stack(6)
        self._data_stack.append(self._return_stack[-4])

    def _word_k(self):
        self._check_return_stack(9)
        self._data_stack.append(self._return_stack[-7])

    def _word_key(self):
        key = get_raw_input(self._in_stream)

        if not key:
            self._data_stack.append(0)
        else:
            if key == '\x03': # Ctrl-C
                raise KeyboardInterrupt()
            self._data_stack.append(ord(key))

    def _word_accept(self):
        self._check_stack(2)
        n1 = self._data_stack.pop()
        addr = self._data_stack.pop()

        _input_buffer = get_input_line(prompt='', stream=self._in_stream, max_length=n1)

        n2 = 0
        if _input_buffer is not None:
            n2 = len(_input_buffer)

        for i in range(n2):
            self._memory[addr + i] = ord(_input_buffer[i])

        self._data_stack.append(n2)


    def _word_refill(self):
        _input_buffer = get_input_line(prompt=self._prompt, stream=self._in_stream)
        self._to_in_set(0)
        if _input_buffer is None:
            self._source_n_set(0)

            self._data_stack.append(0)
            return

        copy_len = min(self._in_buf_len(), len(_input_buffer))
        for i in range(copy_len):
            self._memory[self._source_addr() + i] = ord(_input_buffer[i])
        self._source_n_set(copy_len)

        self._data_stack.append(-1)

    def _word_parse(self):
        self._check_stack(1)

        c = chr(self._data_stack.pop())
        in_begin = self._to_in()
        if self._get_until_char(c):
            u = self._to_in() - in_begin - 1
        else:
            u = 0

        self._data_stack.append(self._source_addr() + in_begin)
        self._data_stack.append(u)

    def _word_word(self):
        self._check_stack(1)

        c = chr(self._data_stack.pop())
        # 先跳过c
        self._skip_chars(c)

        # 然后找word
        in_begin = self._to_in()
        if self._get_until_char(c):
            u = self._to_in() - in_begin - 1
        else:
            u = self._to_in() - in_begin

        # 复制到PAD中部
        c_addr = T4th.MemAddress.PAD_BUFFER.value + (T4th.MemAddress.PAD_BUFFER_LEN.value // 2)
        self._memory[c_addr] = u
        for i in range(u):
            self._memory[c_addr + 1 + i] = self._memory[self._source_addr() + in_begin + i]

        self._data_stack.append(c_addr)

    def _word_type(self):
        self._check_stack(2)

        u = self._data_stack.pop()
        addr = self._data_stack.pop()

        for i in range(u):
            ch_ord = self._memory[addr + i]
            print(chr(ch_ord), end='', flush=True)

    def _word_to_number(self):
        self._check_stack(4)

        n = self._data_stack.pop()
        addr = self._data_stack.pop()
        u2 = self._data_stack.pop()
        u1 = self._data_stack.pop()

        ud = tn.ud2i(u1, u2)

        i = 0
        while i < n:
            ch = chr(self._memory[addr + i])
            d = tn.ch_to_int(ch)
            if d < 0:
                break
            ud = ud * self._base() + d
            i += 1

        (u1, u2) = tn.i2d(ud)
        self._data_stack.append(u1)
        self._data_stack.append(u2)
        self._data_stack.append(addr + i)
        self._data_stack.append(n - i)

    def _word_source(self):
        self._data_stack.append(self._source_addr())
        self._data_stack.append(self._source_n())


    def _word_save_input(self):
        # 备份状态
        backup = self._input_backup()
        self._data_stack.append(backup)
        self._data_stack.append(1)


    def _word_restore_input(self):
        self._check_stack(2)

        n = self._data_stack.pop()
        if n != 1:
            raise ValueError(f'Invalid number of save-input parameters: {n}')

        backup = self._data_stack.pop()

        self._input_restore(backup)

        # 恢复的结果
        self._data_stack.append(0)

    def _word_included(self):
        self._check_stack(2)

        u = self._data_stack.pop()
        addr = self._data_stack.pop()

        filename = self._copy_counted_str(addr, u)

        f = open(filename, 'r', encoding='utf-8')

        input_backup = self._input_backup()

        try:
            pc = self._pc
            self._in_stream = f
            self._source_n_set(0)
            self._to_in_set(0)

            self.interpret()
        finally:
            f.close()
            self._input_restore(input_backup)
            self._pc = pc


    # 辅助函数

    def _check_stack(self, depth):
        if len(self._data_stack) < depth:
            raise ValueError(f'Stack underflow: {len(self._data_stack)} < {depth}')

    def _check_return_stack(self, depth):
        if len(self._return_stack) < depth:
            raise ValueError(f'Return stack underflow: {len(self._return_stack)} < {depth}')

    def _base(self):
        return self._get_var_value('BASE')

    def _here(self):
        return self._get_var_value('DP')

    def _memory_append(self, v):
        if self._here() >= len(self._memory):
            raise ValueError('Memory overflow')
        self._memory[self._here()] = v
        self._memory[T4th.MemAddress.DP.value] += 1

    def _forget_p(self, p:int):
        w = self._memory[p]
        self._memory[T4th.MemAddress.DP.value] = p
        self._latest_word_ptr = w.prev

    def _copy_counted_str(self, c_addr:int, n:int = -1) -> str:
        if n == -1:
            n = self._memory[c_addr]
            c_addr += 1
        s = ''
        for i in range(n):
            s += chr(self._memory[c_addr + i])
        return s

    def _in_buf_len(self):
        return T4th.MemAddress.IN_BUFFER_LEN.value

    def _source_addr(self):
        return self._get_var_value('SOURCE_P')

    def _source_addr_set(self, v):
        self._set_var_value('SOURCE_P', v)

    def _source_n(self):
        return self._get_var_value('SOURCE_N')

    def _source_n_set(self, v):
        self._set_var_value('SOURCE_N', v)

    def _to_in(self):
        return self._get_var_value('TO_IN')

    def _to_in_inc(self):
        self._inc_var('TO_IN')

    def _to_in_set(self, v):
        self._set_var_value('TO_IN', v)

    def _input_backup(self):
        stream_pos = 0 if not self._in_stream.seekable() else self._in_stream.tell()
        in_stream = self._in_stream

        source_content = self._memory[self._source_addr():self._source_addr() + self._source_n()]
        source_addr = self._source_addr()
        source_n = self._source_n()
        to_in = self._to_in()

        return (stream_pos, in_stream, source_content, source_addr, source_n, to_in)

    def _input_restore(self, backup):
        (stream_pos, in_stream, source_content, source_addr, source_n, to_in) = backup

        self._source_addr_set(source_addr)
        self._source_n_set(source_n)
        self._to_in_set(to_in)
        self._memory[source_addr:source_addr + source_n] = source_content

        self._in_stream = in_stream
        if self._in_stream.seekable():
            self._in_stream.seek(stream_pos)

    # IO函数

    def _skip_chars(self, c):
        while self._to_in() < self._source_n():
            ch_ord = self._memory[self._source_addr() + self._to_in()]
            if chr(ch_ord) != c:
                break

            self._to_in_inc()

    def _get_until_char(self, c) -> bool:
        while self._to_in() < self._source_n():
            ch_ord = self._memory[self._source_addr() + self._to_in()]
            if chr(ch_ord) == c:
                self._to_in_inc()
                return True
            self._to_in_inc()
        return False

    def _get_next_word_or_none(self) -> Optional[str]:
        if self._source_n() == 0:
            _input_buffer = get_input_line(prompt=self._prompt, stream=self._in_stream)
            self._to_in_set(0)
            if _input_buffer is None:
                self._source_n_set(0)
                return None

            # 复制输入内容到memory
            copy_len = min(self._in_buf_len(), len(_input_buffer))
            for i in range(copy_len):
                self._memory[self._source_addr() + i] = ord(_input_buffer[i])
            self._source_n_set(copy_len)

        if self._to_in() >= self._source_n():
            self._to_in_set(0)
            self._source_n_set(0)
            return ''

        word = ''
        while self._to_in() < self._source_n():
            ch_ord = self._memory[self._source_addr() + self._to_in()]
            c = chr(ch_ord)

            self._to_in_inc()
            if not c in [' ', '\t', '\n', '\r']:
                word += c
            else:
                break

        return word

    def _get_next_word(self) -> str:
        word = self._get_next_word_or_none()
        if word is None or word == '':
            raise ValueError('Could not get word name')
        return word

    # VM相关

    def _init_vm(self):
        self._quit = False
        self._quit_on_error = False

        self._data_stack = tn.memory()
        self._return_stack = tn.memory()

        self._memory = tn.memory(self._memory_size)
        self._memory[T4th.MemAddress.DP.value] = T4th.MemAddress.END.value
        self._memory[T4th.MemAddress.BASE.value] = 10

        self._latest_word_ptr = 0 # 0表示无效的指针
        self._set_var_value('STATE', 0)

        self._rescue()

        # Add primitive words to dictionary
        for (w, f) in self._primitive_words:
            w.ptr = self._here() + 1
            self._add_word(w)
            self._memory_append(T4th._PrimitiveWord(w.word_name, f))


    def _rescue(self):
        # 在定义词的过程中恢复
        if self._get_var_value('STATE') != 0 and self._latest_word_ptr > 0:
            # 清理掉最后一个定义的词
            self._forget_p(self._latest_word_ptr)


        self._data_stack.clear()
        self._return_stack.clear()

        self._source_addr_set(T4th.MemAddress.IN_BUFFER_ADDR.value)
        self._source_n_set(0)
        self._to_in_set(0)

        self._pc = 0
        self._exec_pc = 0
        self._set_var_value('STATE', 0)
        self._in_stream = sys.stdin
        self._prompt = ''
        self._evaluating = False

    def interpret(self):
        while not self._quit:
            try:
                word_name = self._get_next_word_or_none()
                if word_name is None:
                    break # End of input

                if not self._evaluating:
                    self._prompt = ' ok\n' if self._get_var_value('STATE') == 0 else ' compiled\n'

                if word_name == '':
                    continue

                self._execute_word(word_name)

            except Exception as e:
                print()
                print(f'Error: {e}')
                self._rescue()
                self._prompt = ''
                if self._quit_on_error:
                    raise e

            except KeyboardInterrupt:
                print()
                print('Use interrupt')
                self._rescue()
                self._prompt = ''

    def _execute_word(self, word_name):
        word = self._find_word_or_none(word_name)

        if word:
            if self._get_var_value('STATE') != 0 and not word.is_immediate():
                self._memory_append(word.ptr)
            else:
                if self._get_var_value('STATE') == 0 and word.is_non_interactive():
                    raise ValueError(f'Non-interactive word "{word_name}"')

                self._pc = T4th.MemAddress.EXEC_START.value
                self._memory[T4th.MemAddress.EXEC_START.value] = word.ptr

                while self._pc != T4th.MemAddress.EXEC_START.value + 1:
                    self._exec_pc = self._memory[self._pc]
                    self._pc += 1
                    self._memory[self._exec_pc]()

        else:
            try:
                d = False
                if word_name[0] == "'": # 字符
                    if len(word_name) != 3 or word_name[2] != "'":
                        raise ValueError(f'Invalid character "{word_name}"')
                    value = ord(word_name[1])
                else:
                    s = 1
                    w = word_name
                    if w[0] == '-':
                        s = -1
                        w = w[1:]

                    b = self._base()

                    if w[0] == '#':
                        b = 10
                        w = w[1:]
                    elif w[0] == '$':
                        b = 16
                        w = w[1:]
                    elif w[0] == '%':
                        b = 2
                        w = w[1:]

                    if len(w) > 0:
                        if w[-1] == '.':
                            d = True
                            w = w[:-1]

                    value = int(w, b) * s

                if self._get_var_value('STATE') != 0:
                    if d:
                        (n1, n2) = tn.i2d(value)
                        self._data_stack.append(n1)
                        self._data_stack.append(n2)
                        self._memory_append(self._find_word('(LITERAL)').ptr)
                        self._memory_append(n1)
                        self._memory_append(self._find_word('(LITERAL)').ptr)
                        self._memory_append(n2)
                    else:
                        self._memory_append(self._find_word('(LITERAL)').ptr)
                        self._memory_append(value)
                else:
                    if d:
                        (n1, n2) = tn.i2d(value)
                        self._data_stack.append(n1)
                        self._data_stack.append(n2)
                    else:
                        self._data_stack.append(value)
            except ValueError:
                raise ValueError(f'Unknown word "{word_name}"')

    def load_and_run_file(self, filename) -> bool:
        self._quit_on_error = True
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self._in_stream = file
                self.interpret()
            self._in_stream = sys.stdin
            self._prompt = ''
        except FileNotFoundError:
            print(f'Error: file "{filename}" not found')
            exit(1)
        finally:
            self._quit_on_error = False

    def _load_core_fs(self):
        # 从本模块同级目录下加载并执行 core.fs 文件的内容
        current_dir = os.path.dirname(__file__)
        self.load_and_run_file(os.path.join(current_dir, 'core.fs'))


def main():
    t4th = T4th()

    t4th._load_core_fs()

    print(f'T4th version {t4th._version} [ Free memory {len(t4th._memory) - t4th._here()} ]')
    t4th.interpret()  # 进入命令交互

if __name__ == '__main__': # pragma: no cover
    main()
