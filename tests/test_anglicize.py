from anglicize import Anglicize


def test_polish() -> None:
    assert Anglicize.anglicize('Cześć!'.encode()).decode() == "Czeshch!"
