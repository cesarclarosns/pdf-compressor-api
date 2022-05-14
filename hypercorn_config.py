from api.app import app
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio


config = Config()
config.bind = ["0.0.0.0:5000"]

asyncio.run(serve(app, config))
