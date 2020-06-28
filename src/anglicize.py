#!/usr/bin/env python3

"""Perform anglicization of text in UTF-8 encoding.

The script works as a filter: it reads UTF-8 characters from its
standard input and writes the result to its standard output.

Alternatively, it can be used as a Python module:

    from anglicize import Anglicize

    print(Anglicize.anglicize(utf8_as_bytes))

See README.md for more details."""

from typing import Dict, Optional, Any


class Anglicize(object):
    """Convert a byte sequence of UTF-8 characters to their English
    transcriptions."""

    def __init__(self) -> None:
        self.__state = Anglicize.XLAT_TREE
        self.__finite_state: Optional[Dict[int, Any]] = None
        self.__buf = bytearray()
        self.__capitalization_mode = False
        self.__first_capital_and_spaces = bytearray()
        self.__output = bytearray()

    @staticmethod
    def anglicize(text: bytes) -> bytearray:
        """Process a whole string and return its anglicized version."""
        anglicize = Anglicize()
        return anglicize.process_buf(text) + anglicize.finalize()

    def process_buf(self, buf: bytes) -> bytearray:
        """Anglicize a buffer. Expect more to come."""
        self.__output = bytearray()
        for byte in buf:
            self.__push_byte(byte)
        return self.__output

    def finalize(self) -> bytearray:
        """Process and return the remainder of the internal buffer."""
        self.__output = bytearray()
        while self.__buf or self.__finite_state:
            self.__skip_buf_byte()
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                self.__output += self.__first_capital_and_spaces
            self.__capitalization_mode = False
        return self.__output

    def __push_byte(self, byte: int) -> None:
        """Input another byte. Return the transliteration when it's ready."""
        # Check if there is no transition from the current state
        # for the given byte.
        if byte not in self.__state:
            if self.__state == Anglicize.XLAT_TREE:
                # We're at the start state, which means that
                # no bytes have been accumulated in the
                # buffer and the new byte also cannot be
                # converted.
                self.__hold_spaces_after_capital(byte)
            else:
                self.__skip_buf_byte()
                self.__push_byte(byte)
        else:
            new_state = self.__state[byte]
            if not new_state[1]:
                self.__state = Anglicize.XLAT_TREE
                self.__finite_state = None
                self.__buf = bytearray()
                self.__hold_first_capital(new_state[0])
            else:
                self.__state = new_state[1]
                if new_state[0]:
                    self.__finite_state = new_state
                    self.__buf = bytearray()
                else:
                    self.__buf.append(byte)

    def __skip_buf_byte(self) -> None:
        """Restart character recognition in the internal buffer."""
        self.__state = Anglicize.XLAT_TREE
        if self.__finite_state:
            self.__hold_first_capital(self.__finite_state[0])
            self.__finite_state = None
            buf = self.__buf
        else:
            self.__hold_spaces_after_capital(self.__buf[0])
            buf = self.__buf[1:]
        self.__buf = bytearray()
        for byte in buf:
            self.__push_byte(byte)

    def __hold_first_capital(self, xlat: bytes) -> None:
        """Check for capitalization mode."""
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                if xlat.istitle():
                    xlat = self.__first_capital_and_spaces + xlat
                    self.__first_capital_and_spaces = bytearray()
                    self.__output += xlat.upper()
                    return
                xlat = self.__first_capital_and_spaces + xlat
            elif xlat.istitle():
                self.__output += xlat.upper()
                return
            self.__capitalization_mode = False
        elif xlat.istitle():
            self.__capitalization_mode = True
            self.__first_capital_and_spaces = bytearray(xlat)
            return
        self.__output += xlat

    def __hold_spaces_after_capital(self, byte: int) -> None:
        """Buffer spaces after the first capital letter."""
        if self.__capitalization_mode:
            if self.__first_capital_and_spaces:
                if byte == 32:
                    self.__first_capital_and_spaces.append(byte)
                    return
                else:
                    self.__capitalization_mode = False
                    self.__output += self.__first_capital_and_spaces
            elif byte != 32:
                self.__capitalization_mode = False
        self.__output.append(byte)

    # This variable is updated by make_xlat_tree.
    XLAT_TREE: Dict[int, Any] = {
        0xC2: [b"", {
            0xAB: [b"\"", None],
            0xBB: [b"\"", None]
        }],
        0xC3: [b"", {
            0x80: [b"A", None],
            0x81: [b"A", None],
            0x82: [b"I", None],
            0x83: [b"A", None],
            0x84: [b"A", None],
            0x85: [b"O", None],
            0x86: [b"A", None],
            0x87: [b"S", {
                0xCC: [b"", {
                    0x87: [b"C", None]
                }]
            }],
            0x88: [b"E", None],
            0x89: [b"E", None],
            0x8A: [b"E", None],
            0x8B: [b"Yo", None],
            0x8C: [b"I", None],
            0x8D: [b"I", None],
            0x8E: [b"I", None],
            0x90: [b"D", None],
            0x91: [b"Ny", {
                0xC3: [b"", {
                    0xB3: [b"Nyo", None]
                }]
            }],
            0x92: [b"O", None],
            0x93: [b"O", None],
            0x94: [b"O", None],
            0x95: [b"O", None],
            0x96: [b"O", None],
            0x98: [b"O", None],
            0x99: [b"U", None],
            0x9A: [b"U", None],
            0x9B: [b"U", None],
            0x9C: [b"U", None],
            0x9E: [b"Th", None],
            0x9F: [b"ss", None],
            0xA0: [b"a", None],
            0xA1: [b"a", None],
            0xA2: [b"i", None],
            0xA3: [b"a", None],
            0xA4: [b"a", None],
            0xA5: [b"o", None],
            0xA6: [b"a", None],
            0xA7: [b"s", {
                0xCC: [b"", {
                    0x87: [b"c", None]
                }]
            }],
            0xA8: [b"e", None],
            0xA9: [b"e", None],
            0xAA: [b"e", None],
            0xAB: [b"yo", None],
            0xAC: [b"i", None],
            0xAD: [b"i", None],
            0xAE: [b"i", None],
            0xB0: [b"d", None],
            0xB1: [b"ny", {
                0xC3: [b"", {
                    0xB3: [b"nyo", None]
                }]
            }],
            0xB2: [b"o", None],
            0xB3: [b"o", None],
            0xB4: [b"o", None],
            0xB5: [b"o", None],
            0xB6: [b"o", None],
            0xB8: [b"o", None],
            0xB9: [b"u", None],
            0xBA: [b"u", None],
            0xBB: [b"u", None],
            0xBC: [b"u", None],
            0xBE: [b"th", None]
        }],
        0xC4: [b"", {
            0x82: [b"A", None],
            0x83: [b"a", None],
            0x84: [b"O", None],
            0x85: [b"o", None],
            0x86: [b"Ch", None],
            0x87: [b"ch", None],
            0x98: [b"E", None],
            0x99: [b"e", None],
            0xA2: [b"G", None],
            0xA3: [b"g", None],
            0xB6: [b"K", None],
            0xB7: [b"k", None],
            0xBB: [b"L", None],
            0xBC: [b"l", None]
        }],
        0xC5: [b"", {
            0x81: [b"W", None],
            0x82: [b"w", None],
            0x83: [b"Ny", None],
            0x84: [b"ny", None],
            0x85: [b"N", None],
            0x86: [b"n", None],
            0x96: [b"R", None],
            0x97: [b"r", None],
            0x9A: [b"Sh", None],
            0x9B: [b"sh", None],
            0x9E: [b"Sh", None],
            0x9F: [b"sh", None],
            0xA0: [b"Sh", None],
            0xA1: [b"sh", None],
            0xA2: [b"T", None],
            0xA3: [b"t", None],
            0xB9: [b"Zh", None],
            0xBA: [b"zh", None],
            0xBB: [b"Zh", None],
            0xBC: [b"zh", None],
            0xBD: [b"S", None],
            0xBE: [b"s", None]
        }],
        0xC6: [b"", {
            0x86: [b"", {
                0xCC: [b"", {
                    0xA7: [b"O", None]
                }]
            }],
            0x8F: [b"", {
                0xCC: [b"", {
                    0xA7: [b"E", None]
                }]
            }],
            0x90: [b"", {
                0xCC: [b"", {
                    0xA7: [b"E", None]
                }]
            }],
            0x97: [b"", {
                0xCC: [b"", {
                    0xA7: [b"I", None]
                }]
            }]
        }],
        0xC8: [b"", {
            0x98: [b"Sh", None],
            0x99: [b"sh", None],
            0x9A: [b"Ts", None],
            0x9B: [b"ts", None],
            0xA8: [b"E", {
                0xCC: [b"", {
                    0x87: [b"E", None]
                }]
            }],
            0xA9: [b"e", {
                0xCC: [b"", {
                    0x87: [b"e", None]
                }]
            }]
        }],
        0xC9: [b"", {
            0x94: [b"", {
                0xCC: [b"", {
                    0xA7: [b"o", None]
                }]
            }],
            0x99: [b"", {
                0xCC: [b"", {
                    0xA7: [b"e", None]
                }]
            }],
            0x9B: [b"", {
                0xCC: [b"", {
                    0xA7: [b"e", None]
                }]
            }],
            0xA8: [b"", {
                0xCC: [b"", {
                    0xA7: [b"i", None]
                }]
            }]
        }],
        0xCE: [b"", {
            0x86: [b"A", None],
            0x91: [b"A", {
                0xCE: [b"", {
                    0x99: [b"E", None],
                    0xA5: [b"AF", None],
                    0xB9: [b"E", None]
                }],
                0xCF: [b"", {
                    0x85: [b"Af", None]
                }]
            }],
            0x92: [b"V", None],
            0x93: [b"G", {
                0xCE: [b"", {
                    0x93: [b"NG", None],
                    0x9A: [b"G", None],
                    0x9E: [b"NX", None],
                    0xA7: [b"NKH", None],
                    0xB3: [b"Ng", None],
                    0xBA: [b"G", None],
                    0xBE: [b"Nx", None]
                }],
                0xCF: [b"", {
                    0x87: [b"Nkh", None]
                }]
            }],
            0x94: [b"D", None],
            0x95: [b"E", {
                0xCE: [b"", {
                    0x99: [b"I", None],
                    0xA5: [b"EF", None],
                    0xB9: [b"I", None]
                }],
                0xCF: [b"", {
                    0x85: [b"Ef", None]
                }]
            }],
            0x96: [b"Zd", None],
            0x97: [b"I", {
                0xCE: [b"", {
                    0x99: [b"I", None],
                    0xA5: [b"IF", None],
                    0xB9: [b"I", None]
                }],
                0xCF: [b"", {
                    0x85: [b"If", None]
                }]
            }],
            0x98: [b"Th", None],
            0x99: [b"I", None],
            0x9A: [b"K", None],
            0x9B: [b"L", None],
            0x9C: [b"M", {
                0xCE: [b"", {
                    0xA0: [b"MB", None]
                }],
                0xCF: [b"", {
                    0x80: [b"Mb", None]
                }]
            }],
            0x9D: [b"N", {
                0xCE: [b"", {
                    0xA4: [b"ND", None]
                }],
                0xCF: [b"", {
                    0x84: [b"Nd", None]
                }]
            }],
            0x9E: [b"X", None],
            0x9F: [b"O", {
                0xCE: [b"", {
                    0x99: [b"I", None],
                    0xA5: [b"U", None],
                    0xB9: [b"I", None]
                }],
                0xCF: [b"", {
                    0x85: [b"U", None]
                }]
            }],
            0xA0: [b"P", None],
            0xA1: [b"R", None],
            0xA3: [b"S", None],
            0xA4: [b"T", {
                0xCE: [b"", {
                    0x96: [b"TZ", None],
                    0xB6: [b"Tz", None]
                }]
            }],
            0xA5: [b"U", {
                0xCE: [b"", {
                    0x99: [b"I", None],
                    0xB9: [b"I", None]
                }]
            }],
            0xA6: [b"F", None],
            0xA7: [b"Kh", None],
            0xA8: [b"Ps", None],
            0xA9: [b"O", {
                0xCE: [b"", {
                    0x99: [b"O", None],
                    0xA5: [b"OI", None],
                    0xB9: [b"O", None]
                }],
                0xCF: [b"", {
                    0x85: [b"Oi", None]
                }]
            }],
            0xAC: [b"a", None],
            0xB1: [b"a", {
                0xCE: [b"", {
                    0xB9: [b"e", None]
                }],
                0xCF: [b"", {
                    0x85: [b"af", None]
                }]
            }],
            0xB2: [b"v", None],
            0xB3: [b"g", {
                0xCE: [b"", {
                    0xB3: [b"ng", None],
                    0xBA: [b"g", None],
                    0xBE: [b"nx", None]
                }],
                0xCF: [b"", {
                    0x87: [b"nkh", None]
                }]
            }],
            0xB4: [b"d", None],
            0xB5: [b"e", {
                0xCE: [b"", {
                    0xB9: [b"i", None]
                }],
                0xCF: [b"", {
                    0x85: [b"ef", None]
                }]
            }],
            0xB6: [b"zd", None],
            0xB7: [b"i", {
                0xCE: [b"", {
                    0xB9: [b"i", None]
                }],
                0xCF: [b"", {
                    0x85: [b"if", None]
                }]
            }],
            0xB8: [b"th", None],
            0xB9: [b"i", None],
            0xBA: [b"k", None],
            0xBB: [b"l", None],
            0xBC: [b"m", {
                0xCF: [b"", {
                    0x80: [b"mb", None]
                }]
            }],
            0xBD: [b"n", {
                0xCF: [b"", {
                    0x84: [b"nd", None]
                }]
            }],
            0xBE: [b"x", None],
            0xBF: [b"o", {
                0xCE: [b"", {
                    0xB9: [b"i", None]
                }],
                0xCF: [b"", {
                    0x85: [b"u", None]
                }]
            }]
        }],
        0xCF: [b"", {
            0x80: [b"p", None],
            0x81: [b"r", None],
            0x82: [b"s", None],
            0x83: [b"s", None],
            0x84: [b"t", {
                0xCE: [b"", {
                    0xB6: [b"tz", None]
                }]
            }],
            0x85: [b"u", {
                0xCE: [b"", {
                    0xB9: [b"i", None]
                }]
            }],
            0x86: [b"f", None],
            0x87: [b"kh", None],
            0x88: [b"ps", None],
            0x89: [b"o", {
                0xCE: [b"", {
                    0xB9: [b"o", None]
                }],
                0xCF: [b"", {
                    0x85: [b"oi", None]
                }]
            }],
            0x95: [b"f", None]
        }],
        0xD0: [b"", {
            0x81: [b"Yo", None],
            0x84: [b"Ye", None],
            0x86: [b"I", {
                0xCC: [b"", {
                    0x88: [b"Yi", None]
                }]
            }],
            0x87: [b"Yi", None],
            0x90: [b"A", None],
            0x91: [b"B", None],
            0x92: [b"V", None],
            0x93: [b"G", None],
            0x94: [b"D", None],
            0x95: [b"E", {
                0xCC: [b"", {
                    0x88: [b"Yo", None]
                }]
            }],
            0x96: [b"Zh", None],
            0x97: [b"Z", None],
            0x98: [b"I", {
                0xCC: [b"", {
                    0x86: [b"J", None]
                }]
            }],
            0x99: [b"J", None],
            0x9A: [b"K", None],
            0x9B: [b"L", None],
            0x9C: [b"M", None],
            0x9D: [b"N", None],
            0x9E: [b"O", None],
            0x9F: [b"P", None],
            0xA0: [b"R", None],
            0xA1: [b"S", None],
            0xA2: [b"T", None],
            0xA3: [b"U", None],
            0xA4: [b"F", None],
            0xA5: [b"Kh", None],
            0xA6: [b"Ts", None],
            0xA7: [b"Ch", None],
            0xA8: [b"Sh", None],
            0xA9: [b"Sch", None],
            0xAA: [b"'", None],
            0xAB: [b"Y", None],
            0xAC: [b"", None],
            0xAD: [b"E", None],
            0xAE: [b"Yu", None],
            0xAF: [b"Ya", None],
            0xB0: [b"a", None],
            0xB1: [b"b", None],
            0xB2: [b"v", None],
            0xB3: [b"g", None],
            0xB4: [b"d", None],
            0xB5: [b"e", {
                0xCC: [b"", {
                    0x88: [b"yo", None]
                }]
            }],
            0xB6: [b"zh", None],
            0xB7: [b"z", None],
            0xB8: [b"i", {
                0xCC: [b"", {
                    0x86: [b"j", None]
                }]
            }],
            0xB9: [b"j", None],
            0xBA: [b"k", None],
            0xBB: [b"l", None],
            0xBC: [b"m", None],
            0xBD: [b"n", None],
            0xBE: [b"o", None],
            0xBF: [b"p", None]
        }],
        0xD1: [b"", {
            0x80: [b"r", None],
            0x81: [b"s", None],
            0x82: [b"t", None],
            0x83: [b"u", None],
            0x84: [b"f", None],
            0x85: [b"kh", None],
            0x86: [b"ts", None],
            0x87: [b"ch", None],
            0x88: [b"sh", None],
            0x89: [b"sch", None],
            0x8A: [b"'", None],
            0x8B: [b"y", None],
            0x8C: [b"", None],
            0x8D: [b"e", None],
            0x8E: [b"yu", None],
            0x8F: [b"ya", None],
            0x91: [b"yo", None],
            0x94: [b"ye", None],
            0x96: [b"i", {
                0xCC: [b"", {
                    0x88: [b"yi", None]
                }]
            }],
            0x97: [b"yi", None]
        }],
        0xD2: [b"", {
            0x90: [b"G", None],
            0x91: [b"g", None]
        }],
        0xE1: [b"", {
            0xB8: [b"", {
                0x88: [b"C", None],
                0x89: [b"c", None],
                0x90: [b"D", None],
                0x91: [b"d", None],
                0x9C: [b"E", None],
                0x9D: [b"e", None],
                0xA8: [b"H", None],
                0xA9: [b"h", None]
            }],
            0xBA: [b"", {
                0x9E: [b"Ss", None]
            }],
            0xBC: [b"", {
                0x80: [b"a", None],
                0x81: [b"a", None],
                0x82: [b"a", None],
                0x83: [b"a", None],
                0x84: [b"a", None],
                0x85: [b"a", None],
                0x86: [b"a", None],
                0x87: [b"a", None],
                0x88: [b"A", None],
                0x89: [b"A", None],
                0x8A: [b"A", None],
                0x8B: [b"A", None],
                0x8C: [b"A", None],
                0x8D: [b"A", None],
                0x8E: [b"A", None],
                0x8F: [b"A", None],
                0x90: [b"e", None],
                0x91: [b"e", None],
                0x92: [b"e", None],
                0x93: [b"e", None],
                0x94: [b"e", None],
                0x95: [b"e", None],
                0x98: [b"E", None],
                0x99: [b"E", None],
                0x9A: [b"E", None],
                0x9B: [b"E", None],
                0x9C: [b"E", None],
                0x9D: [b"E", None],
                0xA0: [b"i", None],
                0xA1: [b"i", None],
                0xA2: [b"i", None],
                0xA3: [b"i", None],
                0xA4: [b"i", None],
                0xA5: [b"i", None],
                0xA6: [b"i", None],
                0xA7: [b"i", None],
                0xA8: [b"I", None],
                0xA9: [b"I", None],
                0xAA: [b"I", None],
                0xAB: [b"I", None],
                0xAC: [b"I", None],
                0xAD: [b"I", None],
                0xAE: [b"I", None],
                0xAF: [b"I", None],
                0xB0: [b"i", None],
                0xB1: [b"i", None],
                0xB2: [b"i", None],
                0xB3: [b"i", None],
                0xB4: [b"i", None],
                0xB5: [b"i", None],
                0xB6: [b"i", None],
                0xB7: [b"i", None],
                0xB8: [b"I", None],
                0xB9: [b"I", None],
                0xBA: [b"I", None],
                0xBB: [b"I", None],
                0xBC: [b"I", None],
                0xBD: [b"I", None],
                0xBE: [b"I", None],
                0xBF: [b"I", None]
            }],
            0xBD: [b"", {
                0x80: [b"o", None],
                0x81: [b"o", None],
                0x82: [b"o", None],
                0x83: [b"o", None],
                0x84: [b"o", None],
                0x85: [b"o", None],
                0x88: [b"O", None],
                0x89: [b"O", None],
                0x8A: [b"O", None],
                0x8B: [b"O", None],
                0x8C: [b"O", None],
                0x8D: [b"O", None],
                0x90: [b"u", None],
                0x91: [b"u", None],
                0x92: [b"u", None],
                0x93: [b"u", None],
                0x94: [b"u", None],
                0x95: [b"u", None],
                0x96: [b"u", None],
                0x97: [b"u", None],
                0x99: [b"U", None],
                0x9B: [b"U", None],
                0x9D: [b"U", None],
                0x9F: [b"U", None],
                0xA0: [b"o", None],
                0xA1: [b"o", None],
                0xA2: [b"o", None],
                0xA3: [b"o", None],
                0xA4: [b"o", None],
                0xA5: [b"o", None],
                0xA6: [b"o", None],
                0xA7: [b"o", None],
                0xA8: [b"O", None],
                0xA9: [b"O", None],
                0xAA: [b"O", None],
                0xAB: [b"O", None],
                0xAC: [b"O", None],
                0xAD: [b"O", None],
                0xAE: [b"O", None],
                0xAF: [b"O", None],
                0xB0: [b"a", None],
                0xB1: [b"a", None],
                0xB2: [b"e", None],
                0xB3: [b"e", None],
                0xB4: [b"i", None],
                0xB5: [b"i", None],
                0xB6: [b"i", None],
                0xB7: [b"i", None],
                0xB8: [b"o", None],
                0xB9: [b"o", None],
                0xBA: [b"u", None],
                0xBB: [b"u", None],
                0xBC: [b"o", None],
                0xBD: [b"o", None]
            }],
            0xBE: [b"", {
                0x80: [b"a", None],
                0x81: [b"a", None],
                0x82: [b"a", None],
                0x83: [b"a", None],
                0x84: [b"a", None],
                0x85: [b"a", None],
                0x86: [b"a", None],
                0x87: [b"a", None],
                0x88: [b"A", None],
                0x89: [b"A", None],
                0x8A: [b"A", None],
                0x8B: [b"A", None],
                0x8C: [b"A", None],
                0x8D: [b"A", None],
                0x8E: [b"A", None],
                0x8F: [b"A", None],
                0x90: [b"i", None],
                0x91: [b"i", None],
                0x92: [b"i", None],
                0x93: [b"i", None],
                0x94: [b"i", None],
                0x95: [b"i", None],
                0x96: [b"i", None],
                0x97: [b"i", None],
                0x98: [b"I", None],
                0x99: [b"I", None],
                0x9A: [b"I", None],
                0x9B: [b"I", None],
                0x9C: [b"I", None],
                0x9D: [b"I", None],
                0x9E: [b"I", None],
                0x9F: [b"I", None],
                0xA0: [b"o", None],
                0xA1: [b"o", None],
                0xA2: [b"o", None],
                0xA3: [b"o", None],
                0xA4: [b"o", None],
                0xA5: [b"o", None],
                0xA6: [b"o", None],
                0xA7: [b"o", None],
                0xA8: [b"O", None],
                0xA9: [b"O", None],
                0xAA: [b"O", None],
                0xAB: [b"O", None],
                0xAC: [b"O", None],
                0xAD: [b"O", None],
                0xAE: [b"O", None],
                0xAF: [b"O", None],
                0xB0: [b"a", None],
                0xB1: [b"a", None],
                0xB2: [b"a", None],
                0xB3: [b"a", None],
                0xB4: [b"a", None],
                0xB6: [b"a", None],
                0xB7: [b"a", None],
                0xB8: [b"A", None],
                0xB9: [b"A", None],
                0xBA: [b"A", None],
                0xBB: [b"A", None],
                0xBC: [b"A", None],
                0xBF: [b"'", None]
            }],
            0xBF: [b"", {
                0x82: [b"i", None],
                0x83: [b"i", None],
                0x84: [b"i", None],
                0x86: [b"i", None],
                0x87: [b"i", None],
                0x88: [b"E", None],
                0x89: [b"E", None],
                0x8A: [b"I", None],
                0x8B: [b"I", None],
                0x8C: [b"I", None],
                0x90: [b"i", None],
                0x91: [b"i", None],
                0x92: [b"i", None],
                0x93: [b"i", None],
                0x96: [b"i", None],
                0x97: [b"i", None],
                0x98: [b"I", None],
                0x99: [b"I", None],
                0x9A: [b"I", None],
                0x9B: [b"I", None],
                0xA0: [b"u", None],
                0xA1: [b"u", None],
                0xA2: [b"u", None],
                0xA3: [b"u", None],
                0xA4: [b"r", None],
                0xA5: [b"r", None],
                0xA6: [b"u", None],
                0xA7: [b"u", None],
                0xA8: [b"U", None],
                0xA9: [b"U", None],
                0xAA: [b"U", None],
                0xAB: [b"U", None],
                0xAC: [b"R", None],
                0xB2: [b"o", None],
                0xB3: [b"o", None],
                0xB4: [b"o", None],
                0xB6: [b"o", None],
                0xB7: [b"o", None],
                0xB8: [b"O", None],
                0xB9: [b"O", None],
                0xBA: [b"O", None],
                0xBB: [b"O", None],
                0xBC: [b"O", None],
                0xBE: [b"'", None]
            }]
        }],
        0xE2: [b"", {
            0x80: [b"", {
                0x98: [b"'", None],
                0x99: [b"'", None],
                0x9C: [b"\"", None],
                0x9D: [b"\"", None]
            }]
        }],
        0x41: [b"", {
            0xCC: [b"", {
                0x80: [b"A", None],
                0x81: [b"A", None],
                0x82: [b"I", None],
                0x83: [b"A", None],
                0x86: [b"A", None],
                0x88: [b"A", None],
                0x8A: [b"O", None],
                0xA7: [b"A", None]
            }]
        }],
        0x42: [b"", {
            0xCC: [b"", {
                0xA7: [b"B", None]
            }]
        }],
        0x43: [b"", {
            0xCC: [b"", {
                0xA7: [b"S", None]
            }]
        }],
        0x45: [b"", {
            0xCC: [b"", {
                0x80: [b"E", None],
                0x81: [b"E", None],
                0x82: [b"E", None],
                0x88: [b"E", None]
            }]
        }],
        0x49: [b"", {
            0xCC: [b"", {
                0x80: [b"I", None],
                0x81: [b"I", None],
                0x82: [b"I", None],
                0x88: [b"Yi", None],
                0xA7: [b"I", None]
            }]
        }],
        0x4D: [b"", {
            0xCC: [b"", {
                0xA7: [b"M", None]
            }]
        }],
        0x4E: [b"", {
            0xCC: [b"", {
                0x83: [b"N", None]
            }]
        }],
        0x4F: [b"", {
            0xCC: [b"", {
                0x80: [b"O", None],
                0x81: [b"O", None],
                0x82: [b"O", None],
                0x88: [b"O", None],
                0xA7: [b"O", None]
            }]
        }],
        0x51: [b"", {
            0xCC: [b"", {
                0xA7: [b"Q", None]
            }]
        }],
        0x53: [b"", {
            0xCC: [b"", {
                0xA7: [b"Sh", None]
            }]
        }],
        0x54: [b"", {
            0xCC: [b"", {
                0xA7: [b"Ts", None]
            }]
        }],
        0x55: [b"", {
            0xCC: [b"", {
                0x80: [b"U", None],
                0x81: [b"U", None],
                0x82: [b"U", None],
                0x88: [b"U", None],
                0xA7: [b"U", None]
            }]
        }],
        0x58: [b"", {
            0xCC: [b"", {
                0xA7: [b"X", None]
            }]
        }],
        0x5A: [b"", {
            0xCC: [b"", {
                0xA7: [b"Z", None]
            }]
        }],
        0x61: [b"", {
            0xCC: [b"", {
                0x80: [b"a", None],
                0x81: [b"a", None],
                0x82: [b"i", None],
                0x83: [b"a", None],
                0x86: [b"a", None],
                0x88: [b"a", None],
                0x8A: [b"o", None],
                0xA7: [b"a", None]
            }]
        }],
        0x62: [b"", {
            0xCC: [b"", {
                0xA7: [b"b", None]
            }]
        }],
        0x63: [b"", {
            0xCC: [b"", {
                0xA7: [b"s", None]
            }]
        }],
        0x65: [b"", {
            0xCC: [b"", {
                0x80: [b"e", None],
                0x81: [b"e", None],
                0x82: [b"e", None],
                0x88: [b"e", None]
            }]
        }],
        0x69: [b"", {
            0xCC: [b"", {
                0x80: [b"i", None],
                0x81: [b"i", None],
                0x82: [b"i", None],
                0x88: [b"yi", None],
                0xA7: [b"i", None]
            }]
        }],
        0x6D: [b"", {
            0xCC: [b"", {
                0xA7: [b"m", None]
            }]
        }],
        0x6E: [b"", {
            0xCC: [b"", {
                0x83: [b"n", None]
            }]
        }],
        0x6F: [b"", {
            0xCC: [b"", {
                0x80: [b"o", None],
                0x81: [b"o", None],
                0x82: [b"o", None],
                0x88: [b"o", None],
                0xA7: [b"o", None]
            }]
        }],
        0x71: [b"", {
            0xCC: [b"", {
                0xA7: [b"q", None]
            }]
        }],
        0x73: [b"", {
            0xCC: [b"", {
                0xA7: [b"sh", None]
            }]
        }],
        0x74: [b"", {
            0xCC: [b"", {
                0xA7: [b"ts", None]
            }]
        }],
        0x75: [b"", {
            0xCC: [b"", {
                0x80: [b"u", None],
                0x81: [b"u", None],
                0x82: [b"u", None],
                0x88: [b"u", None],
                0xA7: [b"u", None]
            }]
        }],
        0x78: [b"", {
            0xCC: [b"", {
                0xA7: [b"x", None]
            }]
        }],
        0x7A: [b"", {
            0xCC: [b"", {
                0xA7: [b"z", None]
            }]
        }]
    }


def main() -> None:
    """Apply anglicization to stdin and print the result to stdout."""

    from sys import stdin, stdout

    anglicize = Anglicize()

    while True:
        data = stdin.buffer.read(4096)
        if not data:
            break
        stdout.buffer.write(anglicize.process_buf(data))

    stdout.buffer.write(anglicize.finalize())


if __name__ == "__main__":
    main()
