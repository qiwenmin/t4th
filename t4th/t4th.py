#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Optional
from enum import Enum
from .input import get_raw_input, get_input_line

class T4th:
    _version = '0.1.0'

    MemAddress = Enum("MemAddress", "EXEC_START DP END", start=0)

    class _WordFunc:
        def __init__(self, word, func):
            self.word = word
            self.func = func
        def __call__(self):
            self.func()
        def __str__(self):
            return f"`{self.word}`"
        def __repr__(self):
            return self.__str__()

    def __init__(self):
        self._primitive_words = {
            'KEY': self._word_key,

            '.S': self._word_dot_s,
            '.': self._word_dot,
            'EMIT': self._word_emit,
            'CR': self._word_cr,
            'DUP': self._word_dup,
            'DROP': self._word_drop,
            'SWAP': self._word_swap,
            'OVER': self._word_over,

            '!': self._word_mem_store,
            '@': self._word_mem_fetch,

            'DP': self._word_dp,

            '>R': self._word_to_r,
            'R>': self._word_r_from,

            '+': self._word_add,
            '-': self._word_sub,
            '*': self._word_mul,
            '/': self._word_div,

            'DOCOL': self._word_docol,
            'EXIT': self._word_exit,
            '(LITERAL)': self._word_literal_p,

            'BYE': self._word_bye,

            ':' : self._word_define,
            ';' : self._word_end_def,

            'CREATE': self._word_create,

            '\'': self._word_tick,
            'EXECUTE': self._word_execute,

            'WORDS': self._word_words,

            '.VM': self._print_vm,
        }

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
        if word in self._dictionary:
            print(f'Error: word "{word}" already defined')
            return
        self._dictionary[word] = self._here()
        self._state = 'defining'
        self._append_func('DOCOL')

    def _here(self):
        return self._memory[T4th.MemAddress.DP.value]

    def _here_plus_one(self):
        self._memory[T4th.MemAddress.DP.value] += 1

    def _append_word_index(self, word):
        self._memory_append(self._dictionary[word])

    def _append_func(self, word):
        fn_idx = self._dictionary[word]
        fn = self._memory[fn_idx]
        self._memory_append(fn)

    def _word_end_def(self):
        self._append_word_index('EXIT')
        self._state = 'running'

    def _word_create(self):
        word = self._get_next_word()
        if not word:
            raise ValueError('missing word name')
        word = word.upper()
        if word in self._dictionary:
            raise ValueError(f'word "{word}" already defined')
        self._dictionary[word] = self._here()

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
        exit(0)

    def _word_tick(self):
        word = self._get_next_word()
        if not word:
            raise ValueError('missing word name')
        xt = self._dictionary.get(word.upper())
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
        for word in self._dictionary:
            print(word, end=' ')

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
        self._memory = [0] * 65536
        self._memory[T4th.MemAddress.DP.value] = T4th.MemAddress.END.value

        self._dictionary = {}

        self._rescue()

        # Add primitive words to dictionary
        for word, func in self._primitive_words.items():
            self._dictionary[word] = self._here()
            self._memory_append(T4th._WordFunc(word, func))

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
        print(f'Data stack: {self._data_stack}')
        print(f'Return stack: {self._return_stack}')
        print(f'Memory: {self._memory[:self._memory[T4th.MemAddress.DP.value]]}')
        print(f'Dictionary: {self._dictionary}')

    def interpret(self):
        while True:
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
        if upper_word in self._dictionary:
            if self._state == 'defining' and upper_word != ';':
                self._append_word_index(upper_word)
            else:
                # Execute the word function
                self._pc = T4th.MemAddress.EXEC_START.value
                self._memory[T4th.MemAddress.EXEC_START.value] = self._dictionary[upper_word]

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
                    self._append_word_index('(LITERAL)')
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
    t4th.load_and_run_file('core.fs')  # 加载并执行 core.fs 文件的内容

    print(f'T4th version {t4th._version} [ Free memory {len(t4th._memory) - t4th._here()} ]')
    t4th.interpret()  # 进入命令交互

if __name__ == '__main__':
    main()
