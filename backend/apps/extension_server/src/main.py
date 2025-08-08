# extension_server.py
import uvicorn

from extension_server.src.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=Config.ALLOWED_ORIGINS, allow_methods=['*'], allow_headers=['*'])


@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=9000, log_level='info')
