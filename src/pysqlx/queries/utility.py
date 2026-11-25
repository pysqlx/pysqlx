"""Validation helpers of the queries."""

from collections.abc import Iterable, Sequence

from ..structures import Column


def check_cols(cols: Iterable[Column], cols_all: Sequence[Column]) -> bool:
    """Check that columns are among the allowed ones.

    :param cols: the columns to check
    :param cols_all: the allowed columns
    :returns: whether every column is one of the allowed columns
    """
    for col in cols:
        if col not in cols_all:
            return False
    return True


def check_order_by_cols(
    cols0: Sequence[Column] | None,
    cols1: Sequence[Column] | None,
) -> bool:
    """Check that no column is used for both sorting directions.

    :param cols0: the columns to sort by in ascending order
    :param cols1: the columns to sort by in descending order
    :returns: whether the two sets of columns have no column in common
    """
    if not all((cols0, cols1)):
        return True

    assert cols0 is not None
    assert cols1 is not None

    for col in cols0:
        if col in cols1:
            return False

    for col in cols1:
        if col in cols0:
            return False

    return True
