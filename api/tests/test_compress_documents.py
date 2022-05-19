import aiofiles
import pytest
import unittest
from base64 import b64decode, b64encode

import os
import sys

sys.path.append("/usr/src/api/")

from app import app as quart_app


@pytest.fixture
def app():
    return quart_app


# """Tests unitarios (de las funciones de ayuda)."""


def test_convert_base64_to_pdf(test_input, expected):
    assert True


def test_compress_pdf():
    assert True


def test_convert_pdf_to_base64():
    assert True


"""Tests funcionales (de la API)."""


@pytest.mark.asyncio
async def test_api_unknown_request(app):
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 404


# Testear si el "archivo_contenido" que se retorna es de un menor tamaño.
@pytest.mark.parametrize(
    "pdf_path",
    [
        "/usr/src/api/tests/samples/{}".format(filename)
        for filename in os.listdir("/usr/src/api/tests/samples")
    ],
)
@pytest.mark.asyncio
async def test_api_pdf_compression(app, pdf_path):
    async with aiofiles.open(pdf_path, "rb+") as f:
        encoded_pdf_uncompressed = b64encode(await f.read())
        test_client = app.test_client()
        data = {
            "archivoNombre": "test.pdf",
            "archivoRuta": "",
            "archivoContenido": encoded_pdf_uncompressed,
        }
        response = await test_client.post("/compress/pdf", json=data)
        result = await response.get_json()
        assert sys.getsizeof(result["archivoContenido"]) < sys.getsizeof(
            encoded_pdf_uncompressed
        )


# """Tests de carga."""


def test_load_api():
    assert True
