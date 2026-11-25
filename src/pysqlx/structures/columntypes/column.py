"""Base class of the columns."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from ..structure import Structure
from .aggregate import Aggregate
from .logicalclause import (
    Between,
    Equal,
    GreaterThan,
    GreaterThanEqual,
    InList,
    IsNotNull,
    IsNull,
    LessThan,
    LessThanEqual,
    Like,
    NotEqual,
)

if TYPE_CHECKING:
    from ..table import Table


class Column(Structure):
    """Base class of the columns.

    Comparing a column with a value using ``==``, ``!=``, ``>``, ``>=``,
    ``<`` or ``<=`` creates a clause to use as the condition of a query.
    Because of that, use ``is`` to check whether two variables hold the same
    column.

    The default value is written into the SQL as it is, so a string needs
    its own quotes: ``default_value="'new'"``.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param default_value: the default value of the column, if any
    :param is_identity: whether the database generates the values of the
        column
    :param is_primary_key: whether the column is part of the primary key
    :param is_prevent_null: whether the column rejects null values. Identity
        and primary key columns always do.
    :raises InvalidArgumentError: if an identity or primary key column is
        given a default value
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        default_value: Any,
        is_identity: bool,
        is_primary_key: bool,
        is_prevent_null: bool,
    ) -> None:
        super().__init__(structure_name="column")

        if is_identity or is_primary_key:
            is_prevent_null = True

        if default_value is not None and any((is_identity, is_primary_key)):
            raise InvalidArgumentError("invalid default value settings")

        self.__column_name = column_name
        self.__table = table
        self.__default_value = default_value
        self.__is_identity = is_identity
        self.__is_primary_key = is_primary_key
        self.__is_prevent_null = is_prevent_null

    @property
    def column_name(self) -> str:
        """Name of the column."""
        return self.__column_name

    @property
    def table(self) -> Table:
        """Table which the column belongs to."""
        return self.__table

    @property
    def default_value(self) -> Any:
        """Default value of the column, or ``None``."""
        return self.__default_value

    @property
    def is_identity(self) -> bool:
        """Whether the database generates the values of the column."""
        return self.__is_identity

    @property
    def is_primary_key(self) -> bool:
        """Whether the column is part of the primary key."""
        return self.__is_primary_key

    @property
    def is_prevent_null(self) -> bool:
        """Whether the column rejects null values."""
        return self.__is_prevent_null

    def get_index(self) -> int:
        """Find the position of the column in its table.

        :returns: the index of the column in the columns of its table
        :raises InvalidArgumentError: if the column was removed from its table
        """
        for index, column in enumerate(self.table.columns):
            if column is self:
                return index

        raise InvalidArgumentError("column is not in its table")

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> Equal:  # type: ignore[override]
        return Equal(lhs=self, rhs=other)

    def __ne__(self, other: object) -> NotEqual:  # type: ignore[override]
        return NotEqual(lhs=self, rhs=other)

    def __gt__(self, other: Any) -> GreaterThan:
        return GreaterThan(lhs=self, rhs=other)

    def __ge__(self, other: Any) -> GreaterThanEqual:
        return GreaterThanEqual(lhs=self, rhs=other)

    def __lt__(self, other: Any) -> LessThan:
        return LessThan(lhs=self, rhs=other)

    def __le__(self, other: Any) -> LessThanEqual:
        return LessThanEqual(lhs=self, rhs=other)

    def is_between(self, value0: Any, value1: Any) -> Between:
        """Create a clause which holds when the column is between two values.

        :param value0: the lower bound
        :param value1: the upper bound
        :returns: the clause
        """
        return Between(column=self, value0=value0, value1=value1)

    def is_in_list(self, val_list: Iterable[Any]) -> InList:
        """Create a clause which holds when the column is one of the values.

        :param val_list: the values to compare the column with
        :returns: the clause
        """
        return InList(column=self, val_list=val_list)

    def is_null(self) -> IsNull:
        """Create a clause which holds when the column is null.

        :returns: the clause
        """
        return IsNull(column=self)

    def is_not_null(self) -> IsNotNull:
        """Create a clause which holds when the column is not null.

        :returns: the clause
        """
        return IsNotNull(column=self)

    def is_like(self, other: Any) -> Like:
        """Create a clause which holds when the column matches a pattern.

        :param other: the pattern, in which ``%`` stands for any sequence of
            characters and ``_`` for any single character
        :returns: the clause
        """
        return Like(column=self, value=other)

    def count(self) -> Aggregate:
        """Create an aggregate which counts the values which are not null.

        :returns: the aggregate
        """
        return Aggregate(function_name="COUNT", column=self)

    def sum(self) -> Aggregate:
        """Create an aggregate which adds up the values.

        :returns: the aggregate
        """
        return Aggregate(function_name="SUM", column=self)

    def avg(self) -> Aggregate:
        """Create an aggregate which averages the values.

        :returns: the aggregate
        """
        return Aggregate(function_name="AVG", column=self)

    def min(self) -> Aggregate:
        """Create an aggregate which gives the smallest value.

        :returns: the aggregate
        """
        return Aggregate(function_name="MIN", column=self)

    def max(self) -> Aggregate:
        """Create an aggregate which gives the largest value.

        :returns: the aggregate
        """
        return Aggregate(function_name="MAX", column=self)
