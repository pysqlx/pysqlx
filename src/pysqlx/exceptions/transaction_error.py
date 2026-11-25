"""Transaction error."""

from .pysqlx_error import PysqlxError


class TransactionError(PysqlxError):
    """Raised when a transaction is started, committed or rolled back wrongly."""
