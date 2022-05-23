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


"""
Tests unitarios (de las funciones de ayuda).
"""


"""
Tests funcionales (de la API).
"""


@pytest.mark.asyncio
async def test_api_unknown_request(app):
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_bad_request_invalid_archivo_ruta(app):
    client = app.test_client()
    data = {
        "archivoNombre": "test.pdf",
        "archivoRuta": "C:\etc\test.pdf",
        "archivoContenido": "",
    }
    response = await client.post("/compress/pdf", json=data)
    assert response.status_code == 402


@pytest.mark.asyncio
async def test_api_invalid_archivo_contenido(app):
    client = app.test_client()
    data = {
        "archivoNombre": "test.pdf",
        "archivoRuta": "",
        "archivoContenido": "....",
    }
    response = await client.post("/compress/pdf", json=data)
    assert response.status_code == 402


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
        uncompressed_b64 = b64encode(await f.read())
        client = app.test_client()
        data = {
            "archivoNombre": "test.pdf",
            "archivoRuta": "",
            "archivoContenido": uncompressed_b64,
        }
        response = await client.post("/compress/pdf", json=data)
        result = await response.get_json()
        assert sys.getsizeof(result["archivoContenido"]) < sys.getsizeof(
            uncompressed_b64
        )


"""
Tests de carga.
"""
