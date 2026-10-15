"""FastAPI exception handlers.

Every error path funnels through here so responses match the shared
ErrorResponse contract (``error``, ``message``, ``request_id``, optional
``details``) and always carry the request id for traceability.

Unhandled exceptions are logged with a stack trace server-side but returned
to the client as a generic, non-sensitive payload.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core import request_context
from app.core.logging_config import get_logger
from app.exceptions.base import APIException
from app.core.constants import REQUEST_ID_HEADER

logger = get_logger(__name__)


def _error_body(
    *,
    error: str,
    message: str,
    request_id: str | None,
    details: Any | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error": error,
        "message": message,
    }
    if request_id:
        body["request_id"] = request_id
    if details is not None:
        body["details"] = details
    return body


def _json_response(
    *, status_code: int, body: dict[str, Any], request_id: str | None
) -> JSONResponse:
    headers: dict[str, str] = {}
    if request_id:
        headers[REQUEST_ID_HEADER] = request_id
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def handle_api_exception(request: Request, exc: APIException) -> JSONResponse:
    """Handle domain exceptions derived from :class:`APIException`."""
    request_id = request_context.get_request_id()
    # Client errors are expected; server errors are noteworthy.
    if exc.status_code >= 500:
        logger.error(
            "api_exception", extra={"error_code": exc.error_code, "status": exc.status_code}
        )
    else:
        logger.info(
            "api_exception", extra={"error_code": exc.error_code, "status": exc.status_code}
        )
    return _json_response(
        status_code=exc.status_code,
        body=_error_body(
            error=exc.error_code,
            message=exc.message,
            request_id=request_id,
            details=exc.details,
        ),
        request_id=request_id,
    )


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI/pydantic request validation failures.

    Pydantic error objects may contain input values; we reduce them to
    location + message to avoid echoing potentially sensitive payloads.
    """
    request_id = request_context.get_request_id()
    issues = [
        {
            "loc": [str(part) for part in err.get("loc", ())],
            "msg": err.get("msg", "invalid value"),
            "type": err.get("type", "value_error"),
        }
        for err in exc.errors()
    ]
    return _json_response(
        status_code=422,
        body=_error_body(
            error="validation_failed",
            message="The request failed validation.",
            request_id=request_id,
            details={"issues": issues},
        ),
        request_id=request_id,
    )


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle framework HTTP exceptions (404, 405, etc.)."""
    request_id = request_context.get_request_id()
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        413: "payload_too_large",
        415: "unsupported_media_type",
        429: "rate_limited",
    }
    error_code = code_map.get(exc.status_code, "http_error")
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return _json_response(
        status_code=exc.status_code,
        body=_error_body(error=error_code, message=message, request_id=request_id),
        request_id=request_id,
    )


async def handle_unexpected_exception(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle any unhandled exception without leaking internals."""
    request_id = request_context.get_request_id()
    logger.exception("unhandled_exception")
    return _json_response(
        status_code=500,
        body=_error_body(
            error="internal_error",
            message="An unexpected error occurred.",
            request_id=request_id,
        ),
        request_id=request_id,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to ``app``."""
    app.add_exception_handler(APIException, handle_api_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)
