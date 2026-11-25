"""Exceptions raised by the package."""

from .connection_failed_error import ConnectionFailedError
from .invalid_argument_error import InvalidArgumentError
from .missing_dependency_error import MissingDependencyError
from .pysqlx_error import PysqlxError
from .transaction_error import TransactionError
from .unsupported_operation_error import UnsupportedOperationError

__all__ = [
    "ConnectionFailedError",
    "InvalidArgumentError",
    "MissingDependencyError",
    "PysqlxError",
    "TransactionError",
    "UnsupportedOperationError",
]
