import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse

from .config import Config
from .exceptions.handlers import register_exception_handlers
from .models import (
    AuthBeginRequest,
    AuthCompleteRequest,
    BeginResponse,
    CompleteResponse,
    RegisterBeginRequest,
    RegisterCompleteRequest,
)
from .services.authentication import finish as auth_finish, start as auth_start
from .services.registration import finish as reg_finish, start as reg_start

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(CORSMiddleware, allow_origins=Config.ALLOWED_ORIGINS, allow_methods=['*'], allow_headers=['*'])

# Security scheme for bearer token
security = HTTPBearer(auto_error=True)


@app.get('/health')
async def health():
    return {'status': 'ok'}


# Dependency to verify bearer token is not empty
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials.credentials:
        raise HTTPException(
            status_code=401, detail='Missing bearer token: Authorization header provided but token is empty'
        )
    return credentials.credentials


@app.post('/register/begin', response_model=BeginResponse)
def register_options(payload: RegisterBeginRequest):
    public_key, challenge_token = reg_start(payload.username)
    return JSONResponse(
        content={
            'publicKey': public_key['publicKey'],
            'challenge_token': challenge_token,
        }
    )


@app.post('/register/complete', response_model=CompleteResponse)
def register_verify(payload: RegisterCompleteRequest):
    reg_finish(payload.attestation, payload.challenge_token)
    return {'status': 'OK'}


@app.post('/authenticate/begin', response_model=BeginResponse)
def authenticate_begin(payload: AuthBeginRequest):
    public_key, challenge_token = auth_start(payload.username)
    return JSONResponse(
        content={
            'publicKey': public_key['publicKey'],
            'challenge_token': challenge_token,
        }
    )


@app.post('/authenticate/complete', response_model=CompleteResponse)
def authenticate_complete(payload: AuthCompleteRequest):
    auth_finish(payload.assertion, payload.challenge_token)
    return JSONResponse(content={'status': 'OK'})


if __name__ == '__main__':
    uvicorn.run(app, port=8000, log_level='info')
