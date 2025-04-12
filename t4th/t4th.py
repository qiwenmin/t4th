#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" === TODOs ===
- [X] 去掉dictionary字典，改用传统链表实现
  - [X] 将word的名字放入memory
  - [X] 添加word的向前链接指针，实现查找word的功能
- [X] 实现测试用例
  - [X] 测试启动和退出
  - [X] 对基本堆栈操作做测试
  - [X] 测试定义新词
- [ ] 支持TEST SUITE
  - [X] 实现注释
    - [X] 实现'('
    - [X] 实现'\\'
  - [X] 实现BASE
  - [ ] S"
    - [ ] C"
    - [ ] COUNT
  - [ ] ENVIRONMENT?
  - [X] DEPTH
  - [X] TRUE
  - [X] FALSE
  - [X] IF/ELSE/THEN
    - [X] >MARK/>RESOLVE
    - [X] 0BRANCH
  - [ ] [IF]
  - [ ] [ELSE]
  - [ ] [THEN]
- [X] 加IMMEDIATE标志，并在vm中使用它
- [X] 实现无限循环
  - [X] 实现'BEGIN'和'AGAIN'
    - [X] 实现'IMMEDIATE'
    - [X] 实现'BRANCH'
- [X] 实现'['和']'
- [X] 实现POSTPONE
- [X] 实现CONSTANT
  - [X] 实现DOES>
- [X] 实现VARIABLE
  - [X] 修复CREATE的运行时行为问题
- [X] FORGET
"""

import os
import sys
from typing import Optional
from enum import Enum
from .input import get_raw_input, get_input_line


def int_to_base(n: int, base: int) -> str:
    if not (2 <= base <= 36):
        raise ValueError("Base must be between 2 and 36")
    if n == 0:
        return '0'

    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    is_negative = n < 0
    n = abs(n)
    res = ""
    while n:
        res = digits[n % base] + res
        n //= base
    return '-' + res if is_negative else res


class T4th:
    _version = '0.1.0'

    MemAddress = Enum("MemAddress", "EXEC_START DP BASE END", start=0)

    def _add_push_int_word(self, name, value):
        fn = lambda: self._data_stack.append(value)
        self._add_word(T4th._Word(name, fn))

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
        if self._state == 'defining':
            p = self._memory[p].prev

        while p > 0 and self._memory[p].word_name!= word_name:
            p = self._memory[p].prev
        return p

    def _find_word_or_none(self, word_name:str) -> Optional[_Word]:
        p = self._find_word_ptr(word_name)
        if p == 0:
            return None
        return self._memory[p]

    def _find_word(self, word_name:str) -> Optional[_Word]:
        word = self._find_word_or_none(word_name)
        if word is None:
            raise ValueError(f"Undefined word: `{word_name}`")
        return word

    def __init__(self, memory_size=65536):
        self._memory_size = memory_size

        IM = T4th._Word.FLAG_IMMEDIATE
        NI = T4th._Word.FLAG_NON_INTERACTIVE

        self._primitive_words = [
            (T4th._Word('.VM'), self._print_vm),

            (T4th._Word('DP'), lambda: self._data_stack.append(T4th.MemAddress.DP.value)),
            (T4th._Word('BASE'), lambda: self._data_stack.append(T4th.MemAddress.BASE.value)),

            (T4th._Word('.S'), self._word_dot_s),
            (T4th._Word('.'), self._word_dot),
            (T4th._Word('EMIT'), self._word_emit),
            (T4th._Word('CR'), self._word_cr),

            (T4th._Word('WORDS'), self._word_words),

            (T4th._Word('DOCOL', flag=NI), self._word_docol),
            (T4th._Word(':'), self._word_define),
            (T4th._Word(';', flag=IM), self._word_end_def),
            (T4th._Word('EXIT', flag=NI), self._word_exit),

            (T4th._Word('(', flag=IM), self._word_paren),
            (T4th._Word('\\', flag=IM), self._word_backslash),

            (T4th._Word('KEY'), self._word_key),

            (T4th._Word('DUP'), self._word_dup),
            (T4th._Word('DROP'), self._word_drop),
            (T4th._Word('SWAP'), self._word_swap),
            (T4th._Word('OVER'), self._word_over),
            (T4th._Word('DEPTH'), self._word_depth),

            (T4th._Word('!'), self._word_mem_store),
            (T4th._Word('@'), self._word_mem_fetch),
            (T4th._Word(','), self._word_comma),

            (T4th._Word('>R'), self._word_to_r),
            (T4th._Word('R>'), self._word_r_from),

            (T4th._Word('+'), self._word_add),
            (T4th._Word('-'), self._word_sub),
            (T4th._Word('*'), self._word_mul),
            (T4th._Word('/'), self._word_div),

            (T4th._Word('LITERAL', flag=IM|NI), self._word_literal),
            (T4th._Word('(LITERAL)', flag=NI), self._word_literal_p),

            (T4th._Word(']'), self._word_right_bracket),
            (T4th._Word('[', flag=IM|NI), self._word_left_bracket),

            (T4th._Word('IMMEDIATE', flag=IM), self._word_immediate),

            (T4th._Word('BRANCH', flag=NI), self._word_branch),
            (T4th._Word('0BRANCH', flag=NI), self._word_0branch),

            (T4th._Word('BYE'), self._word_bye),

            (T4th._Word('(CREATE)', flag=NI), self._word_create_p),
            (T4th._Word('CREATE'), self._word_create),

            (T4th._Word('DOES>', flag=NI), self._word_does),

            (T4th._Word('\''), self._word_tick),
            (T4th._Word('EXECUTE'), self._word_execute),

            (T4th._Word('POSTPONE', flag=IM|NI), self._word_postpone),

            (T4th._Word('FORGET'), self._word_forget),
        ]

        self._init_vm()

    def _check_stack(self, depth):
        if len(self._data_stack) < depth:
            raise ValueError(f'Stack underflow: {len(self._data_stack)} < {depth}')

    def _word_paren(self):
        if not self._get_until_char(')'):
            raise ValueError('Unclosed parenthesis')

    def _word_backslash(self):
        self._input_pos = len(self._input_buffer)

    def _word_key(self):
        key = get_raw_input(self._in_stream)

        if not key:
            self._data_stack.append(0)
        else:
            if key == '\x03': # Ctrl-C
                raise KeyboardInterrupt()
            self._data_stack.append(ord(key))

    def _word_dot_s(self):
        print(f'<{len(self._data_stack)}> ', end='', flush=True)
        for v in self._data_stack:
            print(f'{int_to_base(v, self._base())}', end=' ', flush=True)

    def _word_dot(self):
        self._check_stack(1)

        print(f'{int_to_base(self._data_stack.pop(), self._base())} ', end='', flush=True)

    def _word_emit(self):
        self._check_stack(1)

        print(chr(self._data_stack.pop()), end='', flush=True)

    def _word_cr(self):
        print()

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

    def _word_depth(self):
        self._data_stack.append(len(self._data_stack))

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

    def _word_to_r(self):
        self._check_stack(1)

        self._return_stack.append(self._data_stack.pop())

    def _word_r_from(self):
        self._check_stack(1)

        self._data_stack.append(self._return_stack.pop())

    def _word_add(self):
        self._check_stack(2)

        self._data_stack.append(self._data_stack.pop() + self._data_stack.pop())

    def _word_sub(self):
        self._check_stack(2)

        self._data_stack.append(- (self._data_stack.pop() - self._data_stack.pop()))

    def _word_mul(self):
        self._check_stack(2)

        self._data_stack.append(self._data_stack.pop() * self._data_stack.pop())

    def _word_div(self):
        self._check_stack(2)

        a = self._data_stack.pop()
        b = self._data_stack.pop()
        if b == 0:
            raise ValueError('Division by zero')

        self._data_stack.append(b // a)

    def _word_docol(self):
        self._return_stack.append(self._pc)
        self._pc = self._exec_pc + 1

    def _word_define(self):
        word_name = self._get_next_word()

        docol = self._find_word('DOCOL')
        w = T4th._Word(word_name, self._here() + 1, prev=self._latest_word_ptr)
        self._add_word(w)
        self._memory_append(self._memory[docol.ptr])

        self._state = 'defining'

    def _word_exit(self):
        if len(self._return_stack) == 0:
            raise ValueError('Return stack empty')

        self._pc = self._return_stack.pop()

    def _word_end_def(self):
        self._memory_append(self._find_word('EXIT').ptr)
        self._state = 'running'

    def _base(self):
        return self._memory[T4th.MemAddress.BASE.value]

    def _here(self):
        return self._memory[T4th.MemAddress.DP.value]

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

    def _word_right_bracket(self):
        self._state = 'defining'

    def _word_left_bracket(self):
        self._state = 'running'

    def _word_immediate(self):
        if self._latest_word_ptr > 0:
            self._memory[self._latest_word_ptr].flag |= T4th._Word.FLAG_IMMEDIATE

    def _word_branch(self):
        self._pc = self._memory[self._pc]

    def _word_0branch(self):
        self._check_stack(1)

        if self._data_stack.pop() == 0:
            self._pc = self._memory[self._pc]
        else:
            self._pc += 1

    def _word_bye(self):
        print()
        self._quit = True

    def _word_tick(self):
        word_name = self._get_next_word()
        w = self._find_word(word_name)
        self._data_stack.append(w.ptr)

    def _word_execute(self):
        self._check_stack(1)

        xt = self._data_stack.pop()
        self._exec_pc = xt
        self._memory[xt]()

    def _word_postpone(self):
        word_name = self._get_next_word()
        w = self._find_word(word_name)
        if w.is_immediate():
            self._memory_append(w.ptr)
        else:
            self._memory_append(self._find_word('(LITERAL)').ptr)
            self._memory_append(w.ptr)
            self._memory_append(self._find_word(',').ptr)

    def _word_forget(self):
        p_begin = self._find_word_ptr('USER-WORD-BEGIN')
        word_name = self._get_next_word()
        p = self._find_word_ptr(word_name)
        if p > p_begin:
            self._forget_p(p)
        else:
            raise ValueError(f'Cannot forget `{word_name}`')

    def _word_words(self):
        print()
        p = self._latest_word_ptr
        while p > 0:
            print(self._memory[p].word_name, end=' ')
            p = self._memory[p].prev

    def _get_until_char(self, c) -> bool:
        while self._input_pos < len(self._input_buffer):
            if self._input_buffer[self._input_pos] == c:
                self._input_pos += 1
                return True
            self._input_pos += 1
        return False

    def _get_next_word_or_none(self) -> Optional[str]:
        if self._input_pos == 0:
            self._input_buffer = get_input_line(prompt=self._prompt, stream=self._in_stream)
            if self._input_buffer is None:
                self._input_buffer = ''
                return None
            self._input_pos = 0

        if self._input_pos >= len(self._input_buffer):
            self._input_pos = 0
            return ''

        word = ''
        while self._input_pos < len(self._input_buffer):
            c = self._input_buffer[self._input_pos]
            self._input_pos += 1
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

    def _memory_append(self, v):
        if self._here() >= len(self._memory):
            raise ValueError('Memory overflow')
        self._memory[self._here()] = v
        self._memory[T4th.MemAddress.DP.value] += 1

    def _init_vm(self):
        self._quit = False
        self._memory = [0] * self._memory_size
        self._memory[T4th.MemAddress.DP.value] = T4th.MemAddress.END.value
        self._memory[T4th.MemAddress.BASE.value] = 10

        self._latest_word_ptr = 0 # 0表示无效的指针
        self._state = 'running'

        self._rescue()

        # Add primitive words to dictionary
        for (w, f) in self._primitive_words:
            w.ptr = self._here() + 1
            self._add_word(w)
            self._memory_append(T4th._PrimitiveWord(w.word_name, f))


    def _rescue(self):
        # 在定义词的过程中恢复
        if self._state == 'defining' and self._latest_word_ptr > 0:
            # 清理掉最后一个定义的词
            self._forget_p(self._latest_word_ptr)


        self._data_stack = []
        self._return_stack = []

        self._input_buffer = ''
        self._input_pos = 0

        self._pc = 0
        self._exec_pc = 0
        self._state = 'running'
        self._in_stream = sys.stdin
        self._prompt = ''

    def _forget_p(self, p:int):
        w = self._memory[p]
        self._memory[T4th.MemAddress.DP.value] = p
        self._latest_word_ptr = w.prev

    def _print_vm(self):
        print()
        print(f' STACK: {self._data_stack}')
        print(f'     R: {self._return_stack}')
        print(f'    PC: {self._pc}')
        print(f' STATE: {self._state}')
        print(f'  BASE: {self._base()}')
        print(f'LATEST: {self._latest_word_ptr}')

        print(f'Memory: {self._memory[:self._memory[T4th.MemAddress.DP.value]]}')

    def interpret(self):
        while not self._quit:
            try:
                word_name = self._get_next_word_or_none()
                if word_name is None:
                    break # End of input

                self._prompt = ' ok\n' if self._state == 'running' else ' compiled\n'

                if word_name == '':
                    continue

                self._execute_word(word_name)

            except Exception as e:
                print()
                print(f'Error: {e}')
                self._rescue()
                self._prompt = ''
            except KeyboardInterrupt:
                print()
                print('Use interrupt')
                self._rescue()
                self._prompt = ''

    def _execute_word(self, word_name):
        word = self._find_word_or_none(word_name)

        if word:
            if self._state == 'defining' and not word.is_immediate():
                self._memory_append(word.ptr)
            else:
                if self._state == 'running' and word.is_non_interactive():
                    raise ValueError(f'Non-interactive word "{word_name}"')

                self._pc = T4th.MemAddress.EXEC_START.value
                self._memory[T4th.MemAddress.EXEC_START.value] = word.ptr

                while self._pc != T4th.MemAddress.EXEC_START.value + 1:
                    self._exec_pc = self._memory[self._pc]
                    self._pc += 1
                    self._memory[self._exec_pc]()

        else:
            try:
                s = 1
                if word_name[0] == '-':
                    s = -1
                    word_name = word_name[1:]

                b = self._base()

                if word_name[0] == '#':
                    b = 10
                    word_name = word_name[1:]
                elif word_name[0] == '$':
                    b = 16
                    word_name = word_name[1:]

                value = int(word_name, b) * s

                if self._state == 'defining':
                    self._memory_append(self._find_word('(LITERAL)').ptr)
                    self._memory_append(value)
                else:
                    self._data_stack.append(value)
            except ValueError:
                raise ValueError(f'Unknown word "{word_name}"')

    def load_and_run_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self._in_stream = file
                self.interpret()
            self._in_stream = sys.stdin
            self._prompt = ''
        except FileNotFoundError:
            print(f'Error: file "{filename}" not found')
            exit(1)

def main():
    t4th = T4th()

    # 从本模块同级目录下加载并执行 core.fs 文件的内容
    current_dir = os.path.dirname(__file__)
    t4th.load_and_run_file(os.path.join(current_dir, 'core.fs'))

    print(f'T4th version {t4th._version} [ Free memory {len(t4th._memory) - t4th._here()} ]')
    t4th.interpret()  # 进入命令交互

if __name__ == '__main__':
    main()
