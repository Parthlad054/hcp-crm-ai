"""
core/error_handlers.py — Centralised FastAPI exception handler registration.

Extracted from app/main.py so that main.py stays lean.
Call register_error_handlers(app) once during app startup.
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": msg,
            "data": None,
            "detail": msg,
        },
    )


from fastapi.encoders import jsonable_encoder


async def _validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    raw_errors = exc.errors()
    msg = raw_errors[0].get("msg", "Validation error") if raw_errors else "Validation error"
    serializable_errors = jsonable_encoder(raw_errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": f"Validation error: {msg}",
            "data": serializable_errors,
            "detail": serializable_errors,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application."""
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
