"""Invalid argument error."""

from .pysqlx_error import PysqlxError


class InvalidArgumentError(PysqlxError, ValueError):
    """Raised when an argument has an invalid value or type."""
