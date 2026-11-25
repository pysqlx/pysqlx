"""Insert query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..exceptions import InvalidArgumentError
from ..structures import Column, Table
from .query import Query
from .utility import check_cols

if TYPE_CHECKING:
    from ..clients.client import Client


class Insert(Query):
    """Query which adds rows to a table.

    The values of the columns are given when the query is executed.

    :param client: the client which executes the query
    :param table: the table to add rows to
    :param columns: the columns which values are given for. All columns of
        the table by default.
    :raises InvalidArgumentError: if the columns are empty or invalid
    """

    def __init__(
        self,
        client: Client,
        table: Table,
        columns: Sequence[Column] | None,
    ) -> None:
        super().__init__(client=client)

        if columns is None:
            columns = table.columns

        if len(columns) < 1:
            raise InvalidArgumentError("empty columns")

        if not check_cols(columns, table.columns):
            raise InvalidArgumentError("invalid columns")

        self.__table = table
        self.__columns = columns

    @property
    def table(self) -> Table:
        """Table to add rows to."""
        return self.__table

    @property
    def columns(self) -> Sequence[Column]:
        """Columns which values are given for."""
        return self.__columns

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> None:
        super().execute(parameters)

    @override
    def execute_many(self, parameters_list: Sequence[Sequence[Any]]) -> None:
        super().execute_many(parameters_list)
