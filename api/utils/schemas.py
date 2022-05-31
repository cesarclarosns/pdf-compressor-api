from dataclasses import dataclass


@dataclass
class DocumentRequest:
    archivo_nombre: str
    archivo_ruta: str
    archivo_contenido: str


@dataclass
class DocumentResponse:
    resultado: str
    info: str
    error: str
    archivo_nombre: str
    archivo_ruta: str
    archivo_contenido: str
    compresion: str
