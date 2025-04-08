# -*- coding: utf-8 -*-

import sys
from wcwidth import wcwidth
from typing import Optional

if sys.platform == 'win32':
    import msvcrt

    def get_raw_input(stream):
        if stream.isatty():
            ch = msvcrt.getwch()
            return ch
        else:
            ch = stream.read(1)
            return ch
else:
    import tty
    import termios

    def get_raw_input(stream):
        if stream.isatty():
            old_settings = termios.tcgetattr(stream)
            try:
                tty.setraw(stream.fileno())
                ch = stream.read(1)
            finally:
                termios.tcsetattr(stream, termios.TCSADRAIN, old_settings)
            return ch
        else:
            return stream.read(1)

class NullIO:
    def write(self, *args, **kwargs):
        pass

    def flush(self, *args, **kwargs):
        pass

def _move_cursor_left(cursor_pos, display_widths, out_stream) -> int:
    if cursor_pos > 0:
        print('\033[D'*display_widths[cursor_pos-1], end='', flush=True, file=out_stream)
        cursor_pos -= 1
    return cursor_pos

def _move_cursor_right(cursor_pos, display_widths, out_stream, result) -> int:
    if cursor_pos < len(result):
        print('\033[C'*display_widths[cursor_pos], end='', flush=True, file=out_stream)
        cursor_pos += 1
    return cursor_pos

def get_input_line(prompt: str = '', stream=sys.stdin) -> Optional[str]:
    if stream.isatty():
        _out = sys.stdout
    else:
        _out = NullIO()

    print(prompt, end='', flush=True, file=_out)
    result = ''
    cursor_pos = 0
    display_widths = []  # 每个字符的显示宽度（用于计算光标位置）

    while True:
        ch = get_raw_input(stream)

        if ch == '':  # EOF
            return None
        elif ch == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif ch == '\x04':  # Ctrl+D
            return None
        elif ch in ('\n', '\r'):
            print(' ', end='', flush=True, file=_out)
            break
        elif ch in ('\b', '\x7f'):
            if cursor_pos > 0:
                width = display_widths.pop(cursor_pos - 1)
                result = result[:cursor_pos - 1] + result[cursor_pos:]
                cursor_pos -= 1
                print('\b' * width, end='', flush=True, file=_out)
                print(' ' * (sum(display_widths[cursor_pos:]) + width), end='', flush=True, file=_out)
                print('\b' * (sum(display_widths[cursor_pos:]) + width), end='', flush=True, file=_out)
                print(result[cursor_pos:], end='', flush=True, file=_out)
                print('\b' * sum(display_widths[cursor_pos:]), end='', flush=True, file=_out)
        elif ord(ch) == 224:  # Windows系统下的方向键
            ch2 = get_raw_input(stream)
            if ch2 == 'M':  # Right arrow
                cursor_pos = _move_cursor_right(cursor_pos, display_widths, _out, result)
            elif ch2 == 'K':  # Left arrow
                cursor_pos = _move_cursor_left(cursor_pos, display_widths, _out)

        elif ch == '\x1b':  # Escape sequence
            ch2 = get_raw_input(stream)
            if ch2 == '[':
                ch3 = get_raw_input(stream)
                if ch3 == 'C':  # Right arrow
                    cursor_pos = _move_cursor_right(cursor_pos, display_widths, _out, result)
                elif ch3 == 'D':  # Left arrow
                    cursor_pos = _move_cursor_left(cursor_pos, display_widths, _out)
        elif ch.isprintable():
            width = wcwidth(ch)
            if width <= 0:
                continue
            result = result[:cursor_pos] + ch + result[cursor_pos:]
            display_widths.insert(cursor_pos, width)
            print(ch + result[cursor_pos+1:], end='', flush=True, file=_out)
            print('\b' * sum(display_widths[cursor_pos+1:]), end='', flush=True, file=_out)
            cursor_pos += 1
        # 其他不可打印字符，如Ctrl+键，忽略

    return result


if __name__ == '__main__':
    while True:
        try:
            line = get_input_line('> ')
            print()
            print(f'You entered: {line}, length: {len(line)}')
        except KeyboardInterrupt:
            print()
            break
