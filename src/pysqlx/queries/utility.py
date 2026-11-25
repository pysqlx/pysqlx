"""Validation helpers of the queries."""

from collections.abc import Iterable, Sequence

from ..structures import Column


def has_col(col: Column, cols_all: Iterable[Column]) -> bool:
    """Check that a column is among the allowed ones.

    Columns are compared by identity, because ``==`` on a column creates a
    clause.

    :param col: the column to check
    :param cols_all: the allowed columns
    :returns: whether the column is one of the allowed columns
    """
    return any(col is other for other in cols_all)


def check_cols(cols: Iterable[Column], cols_all: Sequence[Column]) -> bool:
    """Check that columns are among the allowed ones.

    :param cols: the columns to check
    :param cols_all: the allowed columns
    :returns: whether every column is one of the allowed columns
    """
    return all(has_col(col, cols_all) for col in cols)


def check_order_by_cols(
    cols0: Sequence[Column] | None,
    cols1: Sequence[Column] | None,
) -> bool:
    """Check that no column is used for both sorting directions.

    :param cols0: the columns to sort by in ascending order
    :param cols1: the columns to sort by in descending order
    :returns: whether the two sets of columns have no column in common
    """
    if not cols0 or not cols1:
        return True

    return not any(has_col(col, cols1) for col in cols0)
