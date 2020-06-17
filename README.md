About
=====

``anglicize.py`` is a Python module (and a script) that performs
[anglicization](https://en.wikipedia.org/wiki/Anglicisation "Anglicisation")
of mixed-language text using a dictionary of phonetic transliterations.

This module accepts UTF-8 text encoded as a sequence of bytes and converts it
to a sequence of the 26 letters of the English alphabet. Unrecognized UTF-8
characters are relayed in unmodified form. The quality of output can be
improved to a degree by defining transliterations for pairs or triplets of
input characters -- suggestions are welcome.

Usage as a script
=================

When used as a script, ``anglicize.py`` works as a filter: it reads UTF-8
data from its standard input, converts the characters it recognizes to the
English alphabet, and prints the result to its standard output.

For example:

    $ ./anglicize.py < INPUT_FILE > OUTPUT_FILE

    $ echo 'Cześć!' | ./anglicize.py
    Czeshch!

Usage as a module
=================

To use ``anglicize.py`` as a module, first import the ``Anglicize``
class from it:

    from anglicize import Anglicize

The class has two modes of operation:

1.  Convert the entire text in one go. This mode works best for texts that
    are already in memory or will have to be loaded in memory anyway. For
    that, there's a static method ``anglicize()``:

        result = Anglicize.anglicize(utf8_string_as_bytes)

    Note that Unicode strings first must be converted to UTF-8 byte strings
    using ``str.encode()`` before they can be passed to the method:

        result = Anglicize.anglicize('retour de la même idée'.encode('UTF-8'))

2.  Convert a large block of text iteratively, one buffer at a time. This
    mode is meant for processing a stream of text data; it consists of
    three steps:

    1.  Create an object of the Anglicize class. This object will keep the
        current state of the finite state machine and a couple of small
        buffers:

            anglicize = Anglicize()
            result = bytearray()

    2.  Pump the data through the object:

            while input.has_data():
                result += anglicize.process_buf(input.read_buffer())

    3.  Finalize processing by flushing the internal buffers of the object:

            result += anglicize.finalize()

How this script came to be
==========================

The original intent of this script was to solve a problem with syncing
files with diacritics in their names between OS X and Linux systems.
The problem is that HFS+ in OS X uses a canonical decomposition
of Unicode characters (a variant of Normal Form D, see
https://developer.apple.com/library/mac/qa/qa1173/).

When a synchronization tool (such as Unison or BitTorrent Sync) copies
a file with diacritics in its name from a Linux system to OS X, the latter
saves the file under a file name that uses NFD decomposition. The next
run of Unison assumes that this is a new file and that the original
file has been deleted, which messes things up. For information about
Unicode normalization, see http://www.unicode.org/faq/normalization.html.

While there are other ways to get around this issue, a decision was made
to write a script to remove any non-ASCII characters from the file names
altogether, which solves the problem once and for all.
