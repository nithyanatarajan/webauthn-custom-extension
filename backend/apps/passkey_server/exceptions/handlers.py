from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

from .errors import ExtensionValidationError


async def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


async def handle_validation_exception(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={'detail': exc.errors()})


async def handle_extension_validation_exception(request: Request, exc: ExtensionValidationError):
    return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={'detail': str(exc)})


async def handle_generic_bad_request(request: Request, exc: ValueError):
    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={'detail': str(exc)})


async def handle_generic_exception(request: Request, exc: Exception):
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': 'Internal Server Error'})


def register_exception_handlers(app):
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(ExtensionValidationError, handle_extension_validation_exception)
    app.add_exception_handler(ValueError, handle_generic_bad_request)
    app.add_exception_handler(Exception, handle_generic_exception)
