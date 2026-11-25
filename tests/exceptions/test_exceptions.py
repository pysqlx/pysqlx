import pytest

from pysqlx.exceptions import (
    ConnectionFailedError,
    InvalidArgumentError,
    MissingDependencyError,
    PysqlxError,
    TransactionError,
    UnsupportedOperationError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        ConnectionFailedError,
        InvalidArgumentError,
        MissingDependencyError,
        TransactionError,
        UnsupportedOperationError,
    ],
)
def test_exceptions_hierarchy(error_type: type[PysqlxError]) -> None:
    assert issubclass(error_type, PysqlxError)
    assert issubclass(error_type, RuntimeError)


def test_exceptions_builtin_bases() -> None:
    assert issubclass(InvalidArgumentError, ValueError)
    assert issubclass(MissingDependencyError, ImportError)
