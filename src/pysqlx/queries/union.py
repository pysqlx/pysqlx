"""Union query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..exceptions import InvalidArgumentError
from ..structures import Clause, Column, Table
from .query import Query
from .select import Select
from .utility import check_cols, check_order_by_cols

if TYPE_CHECKING:
    from ..clients.client import Client


class Union(Query):
    """Query which combines the rows of several select queries.

    :param client: the client which executes the query
    :param table_list: the tables which the select queries read from
    :param query_list: the select queries to combine, one per table
    :param columns_list: the columns to read from each select query. All
        columns of the matching table by default.
    :param is_all: whether to keep duplicate rows
    :param ascend_by: the columns of the first table to sort by in ascending
        order
    :param descend_by: the columns of the first table to sort by in descending
        order
    :param condition: the condition which the rows satisfy
    :raises InvalidArgumentError: if an argument is invalid
    """

    def __init__(
        self,
        client: Client,
        table_list: Sequence[Table],
        query_list: Sequence[Select],
        columns_list: Sequence[Sequence[Column] | None] | None,
        is_all: bool,
        ascend_by: Sequence[Column] | None,
        descend_by: Sequence[Column] | None,
        condition: Clause | None,
    ) -> None:
        super().__init__(client=client)

        if not table_list:
            raise InvalidArgumentError("empty table_list")

        if not query_list:
            raise InvalidArgumentError("empty query_list")

        if len(query_list) != len(table_list):
            raise InvalidArgumentError("query_list and table_list size mismatch")

        for query in query_list:
            if not isinstance(query, Select):
                raise InvalidArgumentError(f'invalid query of type "{type(query).__name__}"')

        if not columns_list:
            columns_list = [None] * len(table_list)

        if len(columns_list) != len(table_list):
            raise InvalidArgumentError("columns_list and table_list size mismatch")

        resolved_columns_list: list[Sequence[Column]] = []

        for given_columns, structure in zip(columns_list, table_list, strict=True):
            columns = given_columns or structure.columns

            if not check_cols(columns, structure.columns):
                raise InvalidArgumentError("invalid columns")

            resolved_columns_list.append(columns)

        if ascend_by and not check_cols(ascend_by, resolved_columns_list[0]):
            raise InvalidArgumentError("invalid ascend_by")

        if descend_by and not check_cols(descend_by, resolved_columns_list[0]):
            raise InvalidArgumentError("invalid descend_by")

        if not check_order_by_cols(ascend_by, descend_by):
            raise InvalidArgumentError("invalid ascend_by and descend_by")

        if not isinstance(is_all, bool):
            raise InvalidArgumentError(f'invalid is_all "{is_all}"')

        self.__table_list = table_list
        self.__query_list = query_list
        self.__columns_list = resolved_columns_list
        self.__is_all = is_all
        self.__ascend_by = ascend_by
        self.__descend_by = descend_by
        self.__condition = condition

    @property
    def table_list(self) -> Sequence[Table]:
        """Tables which the select queries read from."""
        return self.__table_list

    @property
    def query_list(self) -> Sequence[Select]:
        """Select queries to combine."""
        return self.__query_list

    @property
    def columns_list(self) -> Sequence[Sequence[Column]]:
        """Columns to read from each select query."""
        return self.__columns_list

    @property
    def is_all(self) -> bool:
        """Whether to keep duplicate rows."""
        return self.__is_all

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

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> tuple[tuple[Any, ...], ...]:
        rows: tuple[tuple[Any, ...], ...] = super().execute(parameters)
        return rows
