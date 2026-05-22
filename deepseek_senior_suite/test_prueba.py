import pytest
from prueba import lista

def test_suma_lista():
    assert sum(lista) == 6, "La suma de la lista no es igual a 6"
