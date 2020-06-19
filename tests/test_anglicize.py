from anglicize import Anglicize


def test_polish():
    assert Anglicize.anglicize('Cześć!'.encode()).decode() == "Czeshch!"
