from dataclasses import dataclass


@dataclass
class Archivo:
    archivo_nombre: str
    archivo_ruta: str
    archivo_contenido: str
