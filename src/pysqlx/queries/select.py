"""Select query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..exceptions import InvalidArgumentError
from ..structures import Aggregate, Clause, Column, Join, Table
from .query import Query
from .utility import check_cols, check_order_by_cols, has_col

if TYPE_CHECKING:
    from ..clients.client import Client


class Select(Query):
    """Query which reads rows of a table.

    :param client: the client which executes the query
    :param table: the table to read from
    :param limit: the maximum number of rows to read. All rows by default.
    :param columns: the columns and the aggregates to read. All columns of
        the table, and of the joined tables, by default.
    :param ascend_by: the columns to sort by in ascending order
    :param descend_by: the columns to sort by in descending order
    :param condition: the condition which the rows satisfy
    :param offset: the number of rows to skip before reading
    :param group_by: the columns which define the groups of rows which the
        aggregates are computed over
    :param joins: the tables to join to the table of the query
    :param having: the condition which the groups of rows satisfy, built from
        aggregates
    :raises InvalidArgumentError: if an argument is invalid
    """

    def __init__(
        self,
        client: Client,
        table: Table,
        limit: int | None,
        columns: Sequence[Column | Aggregate] | None,
        ascend_by: Sequence[Column] | None,
        descend_by: Sequence[Column] | None,
        condition: Clause | None,
        offset: int | None = None,
        group_by: Sequence[Column] | None = None,
        joins: Sequence[Join] | None = None,
        having: Clause | None = None,
    ) -> None:
        super().__init__(client=client)

        if limit is not None and (
            isinstance(limit, bool) or not isinstance(limit, int) or limit < 0
        ):
            raise InvalidArgumentError(f'invalid limit "{limit}"')

        if offset is not None and (
            isinstance(offset, bool) or not isinstance(offset, int) or offset < 0
        ):
            raise InvalidArgumentError(f'invalid offset "{offset}"')

        available: list[Column] = list(table.columns)

        for join in joins or ():
            if not isinstance(join, Join):
                raise InvalidArgumentError("invalid joins")

            available += join.table.columns

        if not columns:
            columns = available

        for item in columns:
            column = item.column if isinstance(item, Aggregate) else item

            if column is not None and not has_col(column, available):
                raise InvalidArgumentError("invalid columns")

        if ascend_by and not check_cols(ascend_by, available):
            raise InvalidArgumentError("invalid ascend_by")

        if descend_by and not check_cols(descend_by, available):
            raise InvalidArgumentError("invalid descend_by")

        if not check_order_by_cols(ascend_by, descend_by):
            raise InvalidArgumentError("invalid ascend_by and descend_by")

        if group_by and not check_cols(group_by, available):
            raise InvalidArgumentError("invalid group_by")

        self.__table = table
        self.__top = limit
        self.__columns = columns
        self.__ascend_by = ascend_by
        self.__descend_by = descend_by
        self.__condition = condition
        self.__offset = offset
        self.__group_by = group_by
        self.__joins = joins
        self.__having = having

    @property
    def table(self) -> Table:
        """Table to read from."""
        return self.__table

    @property
    def limit(self) -> int | None:
        """Maximum number of rows to read, or ``None`` for all rows."""
        return self.__top

    @property
    def columns(self) -> Sequence[Column | Aggregate]:
        """Columns and aggregates to read."""
        return self.__columns

    @property
    def ascend_by(self) -> Sequence[Column] | None:
        """Columns to sort by in ascending order, or ``None``."""
        return self.__ascend_by

    @property
    def descend_by(self) -> Sequence[Column] | None:
        """Columns to sort by in descending order, or ``None``."""
        return self.__descend_by

    @property
    def condition(self) -> Clause | None:
        """Condition which the rows satisfy, or ``None``."""
        return self.__condition

    @property
    def offset(self) -> int | None:
        """Number of rows to skip before reading, or ``None``."""
        return self.__offset

    @property
    def group_by(self) -> Sequence[Column] | None:
        """Columns which define the groups of rows, or ``None``."""
        return self.__group_by

    @property
    def joins(self) -> Sequence[Join] | None:
        """Tables joined to the table of the query, or ``None``."""
        return self.__joins

    @property
    def having(self) -> Clause | None:
        """Condition which the groups of rows satisfy, or ``None``."""
        return self.__having

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> tuple[tuple[Any, ...], ...]:
        rows: tuple[tuple[Any, ...], ...] = super().execute(parameters)
        return rows
