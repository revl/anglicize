#!/usr/bin/env python

"""Perform anglicization of UTF-8 text.

This file can be used either as a module or as a standalone
script.

When used as a script, the input text can be sent to the
standard input of the script as well as given in the form
of input files on the command line.

To use the file as a module, first import it, then create
an instance of the Anglicize class, and pass the input text
as an str object to the anglicize() method.

See README.md for more details."""

import xlat_tree


class Anglicize:
    """Convert a byte sequence of UTF-8 characters to their English
    transcriptions."""

    def __init__(self):
        self.__state = xlat_tree.xlat_tree
        self.__finite = ''
        self.__buf = ''

    def anglicize(self, text):
        """Anglicize 'text' and return its anglicized version."""
        anglicized = ''
        for char in text:
            anglicized += self.__push(char)
        return anglicized + self.__finalize()

    def __push(self, char):
        """Update the finite state machine of this object."""
        # Check if there is no transition from the current state
        # for the given character.
        if char not in self.__state:
            if self.__state == xlat_tree.xlat_tree:
                # We're at the start state, which means that
                # no characters have been accumulated in the output
                # buffer and the new character also cannot be
                # converted - return it right away
                return char
            # Make sure self.__finalize() is called
            # *before* self.__push(char).
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
    """Apply anglicization to all standard input files and print the result."""
    import fileinput

    anglicize = Anglicize()

    for line in fileinput.input():
        print line + ':\t' + anglicize.anglicize(line)


if __name__ == "__main__":
    main()
