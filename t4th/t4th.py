#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" === TODOs ===
- [X] 去掉dictionary字典，改用传统链表实现
  - [X] 将word的名字放入memory
  - [X] 添加word的向前链接指针，实现查找word的功能
- [ ] 实现测试用例
  - [X] 测试启动和退出
  - [ ] 对基本堆栈操作做测试
  - [ ] 测试定义新词
- [ ] 实现BASE
- [ ] 支持TEST SUITE
  - [ ] 实现注释
    - [ ] 实现'('
    - [ ] 实现'\'
- [X] 加IMMEDIATE标志，并在vm中使用它
- [ ] 支持无限循环
  - [ ] 实现'BEGIN'和'AGAIN'
- [ ] 实现'['和']'
"""

import os
import sys
from typing import Optional
from enum import Enum
from .input import get_raw_input, get_input_line

class T4th:
    _version = '0.1.0'

    MemAddress = Enum("MemAddress", "EXEC_START DP END", start=0)

    class _WordFunc:
        FLAG_IMMEDIATE = 1 << 0

        def __init__(self, word, func, flag=0):
            self.word = word
            self.func = func
            self.flag = flag
        def __call__(self):
            self.func()
        def __str__(self):
            return f"`{self.word}`{'I' if self.is_immediate() else ''}"
        def __repr__(self):
            return self.__str__()
        def is_immediate(self):
            return (self.flag & T4th._WordFunc.FLAG_IMMEDIATE) != 0

    class _WordHeader:
        def __init__(self, word:str, prev:int):
            self.word = word
            self.prev = prev
        def __str__(self):
            return f"[{self.word} {self.prev}]"
        def __repr__(self):
            return self.__str__()

    def _add_word(self, word:str):
        wh = self._WordHeader(word, self._latest_word_ptr)
        self._memory_append(wh)
        self._latest_word_ptr = self._here()

    def _find_word(self, word:str) -> int:
        p = self._latest_word_ptr
        while p > 0 and self._memory[p-1].word!= word:
            p = self._memory[p-1].prev
        return p

    def __init__(self):
        self._primitive_words = [
            T4th._WordFunc('KEY', self._word_key),

            T4th._WordFunc('.S', self._word_dot_s),
            T4th._WordFunc('.', self._word_dot),
            T4th._WordFunc('EMIT', self._word_emit),
            T4th._WordFunc('CR', self._word_cr),
            T4th._WordFunc('DUP', self._word_dup),
            T4th._WordFunc('DROP', self._word_drop),
            T4th._WordFunc('SWAP', self._word_swap),
            T4th._WordFunc('OVER', self._word_over),

            T4th._WordFunc('!', self._word_mem_store),
            T4th._WordFunc('@', self._word_mem_fetch),

            T4th._WordFunc('DP', self._word_dp),

            T4th._WordFunc('>R', self._word_to_r),
            T4th._WordFunc('R>', self._word_r_from),

            T4th._WordFunc('+', self._word_add),
            T4th._WordFunc('-', self._word_sub),
            T4th._WordFunc('*', self._word_mul),
            T4th._WordFunc('/', self._word_div),

            T4th._WordFunc('DOCOL', self._word_docol),
            T4th._WordFunc('EXIT', self._word_exit),
            T4th._WordFunc('(LITERAL)', self._word_literal_p),

            T4th._WordFunc('BYE', self._word_bye),

            T4th._WordFunc(':', self._word_define),
            T4th._WordFunc(';', self._word_end_def, flag=T4th._WordFunc.FLAG_IMMEDIATE),

            T4th._WordFunc('CREATE', self._word_create),

            T4th._WordFunc('\'', self._word_tick),
            T4th._WordFunc('EXECUTE', self._word_execute),

            T4th._WordFunc('WORDS', self._word_words),

            T4th._WordFunc('.VM', self._print_vm),
        ]


        self._reset_vm()

    def _check_stack(self, depth):
        if len(self._data_stack) < depth:
            raise ValueError(f'Stack underflow: {len(self._data_stack)} < {depth}')

    def _word_key(self):
        key = get_raw_input(self._in_stream)

        if not key:
            self._data_stack.append(0)
        else:
            self._data_stack.append(ord(key))

    def _word_dot_s(self):
        print(f'<{len(self._data_stack)}> ', end='', flush=True)
        for v in self._data_stack:
            print(v, end=' ', flush=True)

    def _word_dot(self):
        self._check_stack(1)

        print(f'{self._data_stack.pop()} ', end='', flush=True)

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

    def _word_dp(self):
        self._data_stack.append(T4th.MemAddress.DP.value)

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
            print('Error: division by zero')
            return
        self._data_stack.append(b // a)

    def _word_define(self):
        word = self._get_next_word()
        if not word:
            print('Error: missing word name')
            return
        word = word.upper()
        self._add_word(word)
        self._state = 'defining'
        self._append_func('DOCOL')

    def _here(self):
        return self._memory[T4th.MemAddress.DP.value]

    def _here_plus_one(self):
        self._memory[T4th.MemAddress.DP.value] += 1

    def _append_func(self, word):
        fn_idx = self._find_word(word)
        fn = self._memory[fn_idx]
        self._memory_append(fn)

    def _word_end_def(self):
        self._memory_append(self._find_word('EXIT'))
        self._state = 'running'

    def _word_create(self):
        word = self._get_next_word()
        if not word:
            raise ValueError('missing word name')
        word = word.upper()
        self._add_word(word)

    def _word_docol(self):
        self._return_stack.append(self._pc)
        self._pc = self._memory[self._pc - 1] + 1

    def _word_exit(self):
        if len(self._return_stack) == 0:
            print('Error: return stack empty')
            return
        self._pc = self._return_stack.pop()

    def _word_literal_p(self):
        value = self._memory[self._pc]
        self._data_stack.append(value)
        self._pc += 1

    def _word_bye(self):
        print()
        self._quit = True

    def _word_tick(self):
        word = self._get_next_word()
        if not word:
            raise ValueError('missing word name')
        xt = self._find_word(word.upper())
        if xt is None:
            raise ValueError(f'unknown word "{word}"')
        self._data_stack.append(xt)

    def _word_execute(self):
        self._check_stack(1)

        xt = self._data_stack.pop()
        fn = self._memory[xt]
        fn()

    def _word_words(self):
        print()
        p = self._latest_word_ptr
        while p > 0:
            print(self._memory[p-1].word, end=' ')
            p = self._memory[p-1].prev

    def _get_next_word(self) -> Optional[str]:
        if self._input_pos >= len(self._input_buffer):
            # self._input_buffer = self._in_stream.readline()
            self._input_buffer = get_input_line(prompt=self._prompt, stream=self._in_stream)
            # print(' ', end='', flush=True)
            if self._input_buffer is None:
                self._input_buffer = ''
                return None
            self._input_pos = 0

        word = ''
        while self._input_pos < len(self._input_buffer):
            c = self._input_buffer[self._input_pos]
            self._input_pos += 1
            if not c in [' ', '\t', '\n', '\r']:
                word += c
            else:
                break

        return word

    def _memory_append(self, v):
        self._memory[self._here()] = v
        self._here_plus_one()

    def _reset_vm(self):
        self._quit = False
        self._memory = [0] * 65536
        self._memory[T4th.MemAddress.DP.value] = T4th.MemAddress.END.value

        self._latest_word_ptr = 0 # 0表示无效的指针

        self._rescue()

        # Add primitive words to dictionary
        for word_func in self._primitive_words:
            self._add_word(word_func.word)
            self._memory_append(word_func)

    def _rescue(self):
        self._data_stack = []
        self._return_stack = []

        self._input_buffer = ''
        self._input_pos = 0

        self._pc = 0
        self._state = 'running'
        self._base = 10
        self._in_stream = sys.stdin
        self._prompt = ''

    def _print_vm(self):
        print()
        print(f' STACK: {self._data_stack}')
        print(f'     R: {self._return_stack}')
        print(f'    PC: {self._pc}')
        print(f' STATE: {self._state}')
        print(f'  BASE: {self._base}')
        print(f'LATEST: {self._latest_word_ptr}')

        print(f'Memory: {self._memory[:self._memory[T4th.MemAddress.DP.value]]}')

    def interpret(self):
        while not self._quit:
            try:
                word = self._get_next_word()
                if word is None:
                    break # End of input
                self._prompt = ' ok\n'
                if word == '':
                    continue

                self._execute_word(word)

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

    def _execute_word(self, word):
        upper_word = word.upper()
        word_ptr = self._find_word(upper_word)

        if word_ptr:
            if (self._state == 'defining') and (not self._memory[word_ptr].is_immediate()):
                self._memory_append(word_ptr)
            else:
                # Execute the word function
                self._pc = T4th.MemAddress.EXEC_START.value
                self._memory[T4th.MemAddress.EXEC_START.value] = word_ptr

                while True:
                    fn_idx = self._memory[self._pc]
                    self._pc += 1
                    fn = self._memory[fn_idx]
                    fn()

                    if not self._return_stack:
                        break # End of execution

        else:
            try:
                value = int(word, self._base)

                if self._state == 'defining':
                    self._memory_append(self._find_word('(LITERAL)'))
                    self._memory_append(value)
                else:
                    self._data_stack.append(value)
            except ValueError:
                raise ValueError(f'Unknown word "{word}"')

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
