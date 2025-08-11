# extension_server.py
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Config
from .logging_config import setup_logging

# Ensure logging is configured even when imported (e.g., in tests)
setup_logging()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=Config.ALLOWED_ORIGINS, allow_methods=['*'], allow_headers=['*'])


@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=9000, log_level='info')
