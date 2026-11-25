"""Insert query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..structures import Column, Table
from .query import Query
from .utility import check_cols

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Insert(Query):
    """Query which adds rows to a table.

    The values of the columns are given when the query is executed.

    :param client: the client which executes the query
    :param structure: the table to add rows to
    :param columns: the columns which values are given for. All columns of
        the table by default.
    :raises RuntimeError: if the columns are empty or invalid
    """

    def __init__(
        self,
        client: IClient,
        structure: Table,
        columns: Sequence[Column] | None,
    ) -> None:
        super().__init__(client=client)

        if columns is None:
            columns = structure.columns

        if len(columns) < 1:
            raise RuntimeError("empty columns")

        if not check_cols(columns, structure.columns):
            raise RuntimeError("invalid columns")

        self.__structure = structure
        self.__columns = columns

    @property
    def structure(self) -> Table:
        """Table to add rows to."""
        return self.__structure

    @property
    def columns(self) -> Sequence[Column]:
        """Columns which values are given for."""
        return self.__columns
