"""Unsupported operation error."""

from .pysqlx_error import PysqlxError


class UnsupportedOperationError(PysqlxError):
    """Raised when a database or a query does not support an operation."""
