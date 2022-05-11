from api.app import app
from api.utils.validation_schemas import Archivo
from base64 import b64decode, b64encode
from quart_schema import validate_request
from Quart import request
from urllib import request as urllib_request

import aiofiles
import asyncio
import os
import subprocess


compress_file = Blueprint("compress_file", __name__, url_prefix="api/v1")


"""Funciones de ayuda."""


async def remove_file(file_path):
    """Elimina el archivo con ruta "file_path"."""
    subprocess.run(["rm", "-rf", file_path])


async def convert_base64_to_pdf(archivo_contenido):
    """Convierte el archivo PDF contenido en base64 en "archivo_contenido"
    a un archivo PDF y lo guarda localmente.
    """
    # Define la ruta local del archivo PDF que será generado
    uncompressed_pdf_path = "{}/uncompressed/{}".format(
        STATIC_PATH, req_body.get("archivo_nombre")
    )

    # Genera el archivo PDF decodificando primero
    async with aiofiles.open(uncompressed_pdf_path, mode="wb") as f:
        await f.write(b64decode(archivo_contenido))
        # Regresa la ruta local del archivo PDF
        return uncompressed_pdf_path


async def get_pdf_from_url(archivo_ruta):
    """
    Descarga y almacena localmente el archivo PDF de la URL en
    "archivo_ruta".
    """
    # Define la ruta local del archivo PDF que será generado
    uncompressed_pdf_path = "{}/uncompressed/{}".format(
        STATIC_PATH, req_body.get("archivo_nombre")
    )

    # Descarga y guarda el archivo localmente
    uncompressed_pdf_path, _ = await urllib_request.urlretrieve(
        archivo_ruta, uncompressed_pdf_path
    )
    # Regresa la ruta local del archivo PDF
    return uncompressed_pdf_path


async def compress_pdf(uncompressed_pdf_path, archivo_nombre):
    """Comprime el archivo PDF con ruta "uncompressed_pdf_path" usando Ghostscript.

    -dPDFSETTINGS= configuration: https://www.ghostscript.com/doc/current/VectorDevices.htm#PSPDF_IN

        -dPDFSETTINGS=/screen -> low-resolution
        -dPDFSETTINGS=/ebook -> medium-resolution
        -dPDFSETTINGS=/prepress -> ?
        -dPDFSETTINGS=/printer -> ?
        -dPDFSETTINGS=/default -> ?
    """
    compressed_pdf_path = "{}/compressed/{}".format(STATIC_PATH, archivo_nombre)

    # Comprimir el archivo PDF.
    params = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dBATCH",
        "-sOutputFile={}".format(uncompressed_pdf_path),
        "{}".format(compressed_pdf_path),
    ]

    proc = await asyncio.create_subprocess_shell(
        params, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if stderr:
        raise BaseException("{0}".format(stderr))
    # Regresar la ruta local del archivo PDF comprimido.
    return compressed_pdf_path


async def convert_pdf_to_base64(compressed_pdf_path):
    # Convertir el archivo PDF comprimido a base64.
    async with aiofiles.open(compressed_pdf_path, "rb") as f:
        encoded_data = b64encode(await f.read())
        return encoded_data


async def handle_compressed_pdf(compressed_pdf_path, is_base64, archivo_nombre):
    """Determinar qué hacer con el archivo comprimido.
    1. Subir el archivo PDF a S3. (x)
    2. Subir el archivo PDF en base64 a S3. (x)
    3. Incluir el archivo PDF en base64 en la respuesta JSON.
    """
    # Convertir el archivo PDF a base64 y regresarlo.
    encoded_data = await convert_pdf_to_base64(compressed_pdf_path)
    return encoded_data


def make_response(
    resultado=None,
    info=None,
    error=None,
    archivo_nombre=None,
    archivo_ruta=None,
    archivo_contenido=None,
):
    return {
        "resultado": resultado if bool(resultado) else "",
        "info": info if bool(info) else "",
        "error": error if bool(error) else "",
        "archivo_nombre": archivo_nombre,
        "archivo_ruta": archivo_ruta if bool(archivo_ruta) else "",
        "archivo_contenido": archivo_contenido if bool(archivo_contenido) else "",
    }


"""Vistas/Rutas."""


@compress_file.route("/compress", methods=["POST"])
@validate_request(Archivo)
async def compress_handler(data: Archivo):
    req_body = await request.get_data()

    # Verificar si request contiene el "archivo_contenido".
    is_base64 = bool(req_body.get("archivo_contenido"))

    # Preparar el archivo PDF para comprimirlo.
    try:
        uncompressed_pdf_path = (
            await convert_base64_to_pdf(req_body.get("archivo_contenido"))
            if is_base64
            else await get_pdf_from_url(req_body.get("archivo_ruta"))
        )
    except BaseException as err:
        return (
            make_response(
                resultado=0,
                info="El archivo no se pudo preparar para ser comprimido.",
                error="Error: {}".format(err),
                archivo_nombre=req_body.get("archivo_nombre"),
                archivo_ruta=req_body.get("archivo_ruta"),
                archivo_contenido=req_body.get("archivo_contenido"),
            ),
            501,
        )
    else:
        # Comprimir el archivo PDF.
        try:
            compressed_pdf_path = await compress_pdf(
                uncompressed_pdf_path, req_body.get("archivo_nombre")
            )
        except BaseException as err:
            return (
                make_response(
                    resultado=-1,
                    info="El archivo PDF no se pudo comprimir.",
                    error="Error: {}".format(err),
                    archivo_nombre=req_body.get("archivo_nombre"),
                    archivo_ruta=req_body.get("archivo_ruta"),
                    archivo_contenido=req_body.get("archivo_contenido"),
                ),
                501,
            )
        else:
            # Hacer algo después de comprimir el archivo PDF.
            try:
                compressed_pdf_encoded = await handle_compressed_pdf(
                    compressed_pdf_path, is_base64, req_body.get("archivo_nombre")
                )
            except BaseException as err:
                return (
                    make_response(
                        resultado=0,
                        info="Error al procesar el archivo PDF comprimido.",
                        error="Error: {}".format(err),
                        archivo_nombre=req_body.get("archivo_nombre"),
                        archivo_ruta=req_body.get("archivo_ruta"),
                        archivo_contenido=req_body.get("archivo_contenido"),
                    ),
                    501,
                )
            else:
                # Regresar una respuesta.
                return (
                    make_response(
                        resultado=1,
                        info="El archivo se procesó correctamente.",
                        archivo_nombre=req_body.get("archivo_nombre"),
                        archivo_ruta="",
                        archivo_contenido=compressed_pdf_encoded,
                    ),
                    200,
                )
    finally:
        # Eliminar los archivos generados, ejecutando este proceso cuando sea posible.
        try:
            app.add_background_task(remove_file(uncompressed_pdf_path))
            app.add_background_task(remove_file(compressed_pdf_path))
        except:
            pass


@compress_file.route("/")
async def index():
    return "Hola."
