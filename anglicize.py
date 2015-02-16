#!/usr/bin/env python

"""Perform anglicization of text in UTF-8 encoding.

The script works as a filter: it reads UTF-8 characters from its
standard input and writes the result to its standard output.

Alternatively, it can be used as a Python module:

    from anglicize import Anglicize

    print Anglicize.anglicize(utf8_bytes)

See README.md for more details."""

import xlat_tree

class Anglicize(object):
    """Convert a byte sequence of UTF-8 characters to their English
    transcriptions."""

    def __init__(self):
        self.__state = xlat_tree.xlat_tree
        self.__finite_state = None
        self.__buf = ''
        self.__capitalization_mode = False
        self.__first_capital_and_spaces = ''

    @staticmethod
    def anglicize(text):
        """Process a whole string and return its anglicized version."""
        anglicize = Anglicize()
        return anglicize.process_buf(text) + anglicize.finalize()

    def process_buf(self, buf):
        """Anglicize a buffer. Expect more to come. Keep state between calls."""
        output = ''
        for byte in buf:
            output += self.push_byte(byte)
        return output

    def push_byte(self, byte):
        """Input another byte. Return the transliteration when it's ready."""
        # Check if there is no transition from the current state
        # for the given byte.
        if byte not in self.__state:
            if self.__state == xlat_tree.xlat_tree:
                # We're at the start state, which means that
                # no bytes have been accumulated in the
                # buffer and the new byte also cannot be
                # converted - return it right away
                return self.__hold_spaces_after_capital(byte)
            return self.__skip_buf_byte() + self.push_byte(byte)

        new_state = self.__state[byte]
        if not new_state[1]:
            self.__state = xlat_tree.xlat_tree
            self.__finite_state = None
            self.__buf = ''
            return self.__hold_first_capital(new_state[0])
        self.__state = new_state[1]
        if new_state[0]:
            self.__finite_state = new_state
            self.__buf = ''
        else:
            self.__buf += byte
        return ''

    def finalize(self):
        """Process and return the remainder of the internal buffer."""
        output = ''
        while self.__buf or self.__finite_state:
            output += self.__skip_buf_byte()
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                output += self.__first_capital_and_spaces
            self.__capitalization_mode = False
        return output

    def __skip_buf_byte(self):
        """Restart character recognition in the internal buffer."""
        self.__state = xlat_tree.xlat_tree
        if self.__finite_state:
            output = self.__hold_first_capital(self.__finite_state[0])
            self.__finite_state = None
            buf = self.__buf
        else:
            output = self.__hold_spaces_after_capital(self.__buf[0])
            buf = self.__buf[1:]
        self.__buf = ''
        for byte in buf:
            output += self.push_byte(byte)
        return output

    def __hold_first_capital(self, xlat):
        """Buffer the first capital letter after a series of lower case ones."""
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                if xlat.istitle():
                    xlat = self.__first_capital_and_spaces + xlat
                    self.__first_capital_and_spaces = ''
                    return xlat.upper()
                xlat = self.__first_capital_and_spaces + xlat
            elif xlat.istitle():
                return xlat.upper()
            self.__capitalization_mode = False
        elif xlat.istitle():
            self.__capitalization_mode = True
            self.__first_capital_and_spaces = xlat
            return ''
        return xlat

    def __hold_spaces_after_capital(self, output):
        """Buffer spaces after the first capital letter."""
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                if output == ' ':
                    self.__first_capital_and_spaces += output
                    return ''
                output = self.__first_capital_and_spaces + output
            elif output == ' ':
                return output
            self.__capitalization_mode = False
        return output

def main():
    """Apply anglicization to the standard input stream and print the result."""

    from sys import stdin, stdout

    anglicize = Anglicize()

    while True:
        line = stdin.readline(1024)
        if not line:
            break
        stdout.write(anglicize.process_buf(line))

    stdout.write(anglicize.finalize())

if __name__ == "__main__":
    main()
