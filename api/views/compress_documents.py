from quart import Blueprint, request
from quart_schema import validate_request, validate_response
from api.utils.models import PDFCompressor
import sys

sys.path.append("/usr/src/api")

from utils import PDFCompressor, DocumentRequest, DocumentResponse


compress_documents = Blueprint("compress_documents", __name__, url_prefix="/compress")


""" Funciones de ayuda """


def make_response(
    resultado: str = "",
    info: str = "",
    error: str = "",
    archivo_nombre: str = "",
    archivo_ruta: str = "",
    archivo_contenido: str = "",
    compresion: str = "",
) -> dict:
    return {
        "resultado": resultado,
        "info": info,
        "error": error,
        "archivo_nombre": archivo_nombre,
        "archivo_ruta": archivo_ruta,
        "archivo_contenido": archivo_contenido,
        "compresion": compresion,
    }


""" Rutas """


@compress_documents.route("/pdf", methods=["POST"])
@validate_request(DocumentRequest)
@validate_response(DocumentResponse)
async def compress_pdf_handler(data: DocumentRequest):
    req_body = await request.get_json()

    compressor = PDFCompressor(
        archivo_contenido=req_body["archivo_contenido"],
        archivo_ruta=req_body["archivo_ruta"],
    )
    compression_result = await compressor.start()

    return (
        make_response(
            resultado=compression_result["resultado"],
            info=compression_result["info"],
            error=compression_result["error"],
            archivo_nombre=req_body["archivo_nombre"],
            archivo_contenido=req_body["archivo_contenido"]
            if compression_result["resultado"] == "0"
            else compressor.compressed_b64,
            archivo_ruta=req_body["archivo_ruta"],
            compresion=""
            if compression_result["resultado"] == "0"
            else "{:.2f}%".format(compressor.compresion),
        ),
        402 if compression_result["resultado"] == "0" else 201,
    )
