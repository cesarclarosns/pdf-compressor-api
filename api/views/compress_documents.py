from base64 import b64decode, b64encode
from quart import Blueprint, request
from quart_schema import QuartSchema, validate_request, validate_response
import aiofiles
import asyncio
import uuid
import os
import sys

sys.path.append("/usr/src/api")

from utils import DocumentRequest, DocumentResponse


compress_documents = Blueprint("compress_documents", __name__, url_prefix="/compress")


""" FUNCIONES DE AYUDA """


async def convert_base64_to_pdf(
    archivo_contenido: str, uncompressed_pdf_path: str
) -> None:
    """Convierte el archivo PDF contenido en base64 en "archivo_contenido"
    a un archivo PDF y lo guarda en la ruta específicada "uncompressed_pdf_path".
    """
    async with aiofiles.open(uncompressed_pdf_path, mode="wb+") as f:
        decoded_data = b64decode(archivo_contenido, validate=True)
        if decoded_data[0:4] != b"%PDF":
            raise ValueError("Falta la firma del archivo PDF.")
        await f.write(decoded_data)


async def compress_pdf(uncompressed_pdf_path: str, compressed_pdf_path: str, quality: str) -> None:
    """Comprime el archivo PDF con ruta "uncompressed_pdf_path" usando Ghostscript.

    -dPDFSETTINGS: https://www.ghostscript.com/doc/current/VectorDevices.htm#PSPDF_IN
        -dPDFSETTINGS=/screen -> Resolución baja (150 dpi)
        -dPDFSETTINGS=/ebook -> Resolución media (300 dpi)
        -dPDFSETTINGS=/prepress ->
        -dPDFSETTINGS=/printer -> ?
        -dPDFSETTINGS=/default -> ?
    """
    params = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/{}".format(quality),
        "-dNOPAUSE",
        "-dBATCH",
        "-sOutputFile={}".format(compressed_pdf_path),
        "{}".format(uncompressed_pdf_path),
    ]
    cmd = " ".join(params)

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()


async def convert_pdf_to_base64(compressed_pdf_path: str) -> bytes:
    """Convierte el archivo PDF comprimido con ruta "compressed_pdf_path" a base64
    y lo retorna."""
    async with aiofiles.open(compressed_pdf_path, "rb+") as f:
        encoded_data = b64encode(await f.read())
        return encoded_data





def make_response(
    resultado: str = "",
    info: str = "",
    error: str = "",
    archivo_nombre: str = "",
    archivo_ruta: str = "",
    archivo_contenido: str = "",
) -> dict:
    return {
        "resultado": resultado,
        "info": info,
        "error": error,
        "archivo_nombre": archivo_nombre,
        "archivo_ruta": archivo_ruta,
        "archivo_contenido": archivo_contenido,
    }


""" VISTAS/RUTAS """


@compress_documents.route("/pdf", methods=["POST"])
@validate_request(DocumentRequest)
@validate_response(DocumentResponse)
async def compress_handler(data: DocumentRequest):
    req_body = await request.get_json()

    try:
        # Crear un directorio temporal el cual será usado para guardar los archivos generados
        # y será destruido al completar el contexto.
        async with aiofiles.tempfile.TemporaryDirectory() as d:

            # Verificar si request contiene el "archivo_contenido".
            is_base64 = bool(req_body["archivo_contenido"])

            # Definir las rutas de los archivos que serán usados o generados.
            uncompressed_pdf_path = (
                os.path.join(d, "{}.pdf".format(str(uuid.uuid4())))
                if is_base64
                else req_body["archivo_ruta"]
            )
            compressed_pdf_path = os.path.join(d, "{}.pdf".format(str(uuid.uuid4())))

            try:
                # Preparar el archivo PDF para comprimirlo.
                if is_base64:
                    await convert_base64_to_pdf(
                        req_body["archivo_contenido"], uncompressed_pdf_path
                    )
                else:
                    if not os.path.exists(uncompressed_pdf_path):
                        raise BaseException("El archivo no existe.")
            except BaseException as err:
                return (
                    make_response(
                        resultado="{}".format(0),
                        info="Error al generar el archivo PDF."
                        if is_base64
                        else "Error al encontrar el archivo en la ruta específicada.",
                        error="Error: {}".format(err),
                        archivo_nombre=req_body["archivo_nombre"],
                        archivo_ruta=req_body["archivo_ruta"],
                        archivo_contenido=req_body["archivo_contenido"],
                    ),
                    501,
                )

            try:
                # Comprimir el archivo PDF.
                await compress_pdf(uncompressed_pdf_path, compressed_pdf_path)
            except BaseException as err:
                return (
                    make_response(
                        resultado="{}".format(-1),
                        info="El archivo PDF no se pudo comprimir.",
                        error="Error: {}".format(err),
                        archivo_nombre=req_body["archivo_nombre"],
                        archivo_ruta=req_body["archivo_ruta"],
                        archivo_contenido=req_body["archivo_contenido"],
                    ),
                    501,
                )

            try:
                # Codificar el archivo PDF a base64.
                compressed_pdf_encoded = await convert_pdf_to_base64(
                    compressed_pdf_path
                )
            except BaseException as err:
                return (
                    make_response(
                        resultado="{}".format(0),
                        info="Error al procesar el archivo PDF comprimido.",
                        error="Error: {}".format(err),
                        archivo_nombre=req_body["archivo_nombre"],
                        archivo_ruta=req_body["archivo_ruta"],
                        archivo_contenido=req_body["archivo_contenido"],
                    ),
                    501,
                )

            # Retornar el archivo PDF en base64 como respuesta.
            return (
                make_response(
                    resultado="{}".format(1),
                    info="El archivo se procesó correctamente.",
                    archivo_nombre=req_body["archivo_nombre"],
                    archivo_ruta="",
                    archivo_contenido=compressed_pdf_encoded,
                ),
                200,
            )
    except BaseException as err:
        return make_response(
            resultado="{}".format(0),
            info="Error al generar el directorio temporal.",
            error="Error: {}".format(err),
        )
