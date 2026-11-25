"""Connection failed error."""

from .pysqlx_error import PysqlxError


class ConnectionFailedError(PysqlxError):
    """Raised when a client cannot connect to its database."""
