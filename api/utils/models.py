from base64 import b64decode, b64encode
from uuid import uuid4
import aiofiles
import asyncio
import os
from sys import getsizeof as sizeof


class File:
    def __init__(self) -> None:
        self.temp_dir = None
        self._input = None
        self._output = None

    @property
    def input(self):
        if self._input is None:
            self._input = os.path.join(self.temp_dir, "{}.pdf".format(str(uuid4())))
        return self._input

    @property
    def output(self):
        if self._output is None:
            self._output = os.path.join(self.temp_dir, "{}.pdf".format(str(uuid4())))
        return self._output

    def new_output(self):
        self._output = os.path.join(self.temp_dir, "{}.pdf".format(str(uuid4())))
        return self._output


class PDFCompressor(File):
    def __init__(self, archivo_contenido: str, archivo_ruta: str) -> None:
        super().__init__()
        self.quality = "ebook"
        self.uncompressed_b64 = archivo_contenido
        self.compressed_b64 = None
        self.archivo_ruta = archivo_ruta

    async def convert_b64_to_pdf(self) -> None:
        try:
            async with aiofiles.open(self.input, mode="wb+") as f:
                decoded_data = b64decode(self.uncompressed_b64, validate=True)
                if decoded_data[0:4] != b"%PDF":
                    raise BaseException("Falta la firma del archivo PDF.")
                await f.write(decoded_data)
        except BaseException as err:
            raise BaseException(
                "El archivo PDF en base64 no se pudo convertir a PDF: {}".format(err)
            )

    async def compress_pdf(self) -> None:
        """
        -dPDFSETTINGS: https://www.ghostscript.com/doc/current/VectorDevices.htm#PSPDF_IN
            -dPDFSETTINGS=/screen: Resolución baja (150 dpi)
            -dPDFSETTINGS=/ebook: Resolución media (300 dpi)
            -dPDFSETTINGS=/prepress: ?
            -dPDFSETTINGS=/printer: ?
            -dPDFSETTINGS=/default: ?
        """
        try:
            params = [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/{}".format(self.quality),
                "-dNOPAUSE",
                "-dBATCH",
                "-sOutputFile={}".format(self.output),
                "{}".format(self.input),
            ]
            cmd = " ".join(params)

            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await proc.communicate()

        except BaseException as err:
            raise BaseException("El archivo PDF no se pudo comprimir: {}".format(err))

    async def convert_pdf_to_b64(self) -> bytes:
        try:
            async with aiofiles.open(self.output, "rb+") as f:
                self.compressed_b64 = b64encode(await f.read())
        except BaseException as err:
            raise BaseException(
                "El archivo PDF no se pudo convertir a base64: {}".format(err)
            )

    async def start(self) -> None:
        try:
            async with aiofiles.tempfile.TemporaryDirectory() as d:
                self.temp_dir = d

                if self.archivo_ruta:
                    if not os.path.exists(self.archivo_ruta):
                        raise BaseException(
                            "El archivo en la ruta específicada no existe: '{}'.".format(self.archivo_ruta)
                        )
                    self._input = self.archivo_ruta
                else:
                    await self.convert_b64_to_pdf()

                await self.compress_pdf()
                await self.convert_pdf_to_b64()
                if sizeof(self.compressed_b64) > sizeof(self.uncompressed_b64):
                    self.quality = "screen"
                    self.new_output()
                    await self.compress_pdf()
                    await self.convert_pdf_to_b64()
                    if sizeof(self.compressed_b64) > sizeof(self.uncompressed_b64):
                        raise BaseException("No se pudo reducir el tamaño del archivo.")

                return {
                    "resultado": "1",
                    "info": "El archivo se procesó correctamente.",
                    "error": "",
                }

        except BaseException as err:
            return {
                "resultado": "0",
                "info": "El archivo no se procesó correctamente.",
                "error": "{}".format(err),
            }
