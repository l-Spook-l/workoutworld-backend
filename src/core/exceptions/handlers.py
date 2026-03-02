import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions.custom_exceptions import AppError

log = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.exception("Unhandled exception")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": "Internal server error"
            },
        )

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError):
        log.error(
            "AppError occurred",
            extra={
                "path": request.url.path,
                "method": request.method,
                "detail": exc.detail,
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "detail": exc.detail,
            },
        )
