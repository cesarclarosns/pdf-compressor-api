import pytest
import unittest
from views.compress_documents import (
    convert_base64_to_pdf,
    compress_pdf,
    convert_pdf_to_base64,
)

"""Tests unitarios (de las funciones de ayuda)."""


@pytest.mark.parametrize("test,expected", [])
def test_convert_base64_to_pdf(test_input, expected):
    assert True


def test_compress_pdf():
    assert True


def test_convert_pdf_to_base64():
    assert True


"""Tests funcionales (de la API)."""

# Testear si el "archivo_contenido" que se retorna es de un menor tamaño.
def test_api():
    assert True


"""Tests de carga."""


def test_load_api():
    assert True
