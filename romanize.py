#!/usr/bin/env python

"""Perform romanization of Russian text.

This file can be used either as a module or as a standalone
script.

When used as a script, the input text can be sent to the
standard input of the script as well as given in the form
of input files on the command line.

To use the file as a module, import it, create an instance
of the Romanize class, and pass the input text as an str
object to the romanize() method."""

import xlat_tree


class Romanize:
    """Convert a byte sequence of UTF-8 characters to their latin
    transcriptions. See https://en.wikipedia.org/wiki/Romanization
    for details."""
    def __init__(self):
        self.__state = xlat_tree.xlat_tree
        self.__finite = ''
        self.__buf = ''

    def romanize(self, text):
        """Romanize the supplied text and return the romanized version."""
        romanized = ''
        for char in text:
            romanized += self.__push(char)
        return romanized + self.__finalize()

    def __push(self, char):
        """Update the finite state machine of this object."""
        if not char in self.__state:
            if self.__state == xlat_tree.xlat_tree:
                return char
            finite = self.__finalize()
            return finite + self.__push(char)
        new_node = self.__state[char]
        if not new_node[1]:
            self.__state = xlat_tree.xlat_tree
            self.__finite = ''
            self.__buf = ''
            return new_node[0]
        self.__state = new_node[1]
        if new_node[0]:
            self.__finite = new_node[0]
            self.__buf = ''
        else:
            self.__buf += char
        return ''

    def __finalize(self):
        """Process bytes accumulated in self.__buf."""
        self.__state = xlat_tree.xlat_tree
        finite = self.__finite
        self.__finite = ''
        if self.__buf:
            buf = self.__buf
            finite += buf[0]
            for char in buf[1:]:
                finite += self.__push(char)
            self.__buf = ''
        return finite


def main():
    """Apply romanization to all standard input files and print the result."""
    import fileinput

    romanize = Romanize()

    for line in fileinput.input():
        print line + ':\t' + romanize.romanize(line)


if __name__ == "__main__":
    main()
