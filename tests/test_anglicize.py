from anglicize import Anglicize


def test_finalize() -> None:
    assert Anglicize.anglicize('γ'.encode()) == b'g'
    assert Anglicize.anglicize('Γ'.encode()) == b'G'


def test_buffering() -> None:
    anglicize = Anglicize()
    output = anglicize.process_buf('Μιλάω '.encode() + 'ε'.encode()[:1])
    output += anglicize.process_buf('ε'.encode()[1:] + 'λληνικά'.encode())
    output += anglicize.finalize()
    assert output == b'Milao ellinika'

    output = anglicize.process_buf('Ja '.encode())
    output += anglicize.process_buf('mówie '.encode())
    output += anglicize.process_buf('po polsku.'.encode())
    output += anglicize.finalize()
    assert output == b'Ja mowie po polsku.'


def test_capitalization() -> None:
    assert Anglicize.anglicize('Cześć!'.encode()) == b'Czeshch!'
    assert Anglicize.anglicize('CZEŚĆ!'.encode()) == b'CZESHCH!'

    assert Anglicize.anglicize('Япония'.encode()) == b'Yaponiya'
    assert Anglicize.anglicize('Я говорю'.encode()) == b'Ya govoryu'
    assert Anglicize.anglicize('ЯЩЕРИЦА'.encode()) == b'YASCHERITSA'
    assert Anglicize.anglicize('Я ЩЕКОЧУ'.encode()) == b'YA SCHEKOCHU'


def test_pass_through_unrecognized_utf8() -> None:
    assert Anglicize.anglicize('¿Adónde?'.encode()) == '¿Adonde?'.encode()
