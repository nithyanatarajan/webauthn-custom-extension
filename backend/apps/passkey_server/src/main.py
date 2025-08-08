import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passkey_server.src.config import Config

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=Config.ALLOWED_ORIGINS, allow_methods=['*'], allow_headers=['*'])


@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=8000, log_level='info')
