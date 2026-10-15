"""Database-related exceptions.

These map low-level SQLAlchemy/driver failures to safe, non-sensitive API
errors. Raw SQL, connection strings and parameter values are never surfaced.
"""

from __future__ import annotations

from typing import Optional

from app.exceptions.base import APIException


class DatabaseError(APIException):
    status_code = 503
    error_code = "database_error"
    default_message = "A database error occurred while processing the request."


class DatabaseUnavailableError(APIException):
    status_code = 503
    error_code = "database_unavailable"
    default_message = "The database is temporarily unavailable."


class RecordNotFoundError(APIException):
    status_code = 404
    error_code = "record_not_found"
    default_message = "The requested record was not found."


class DuplicateRecordError(APIException):
    status_code = 409
    error_code = "duplicate_record"
    default_message = "A record with the same unique fields already exists."


class IntegrityConstraintError(APIException):
    status_code = 409
    error_code = "integrity_constraint_violated"
    default_message = "The operation violates a data integrity constraint."


class MigrationRequiredError(APIException):
    status_code = 503
    error_code = "migration_required"
    default_message = "The database schema is not up to date."

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message)
