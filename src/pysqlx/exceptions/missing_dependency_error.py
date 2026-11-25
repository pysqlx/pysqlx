"""Missing dependency error."""

from .pysqlx_error import PysqlxError


class MissingDependencyError(PysqlxError, ImportError):
    """Raised when the library which a client needs is not installed."""
