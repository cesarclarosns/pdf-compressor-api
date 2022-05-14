from quart import Blueprint
from .compress_documents import compress_documents

blueprints = [compress_documents]
