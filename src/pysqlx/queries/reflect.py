"""Reflect query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Reflect(Query):
    """Query which reads the columns of a table from the database.

    The result is a table with the columns found in the database, to use in
    other queries. Foreign keys are not read.

    :param client: the client which executes the query
    :param structure: the table to read the columns of, given without
        columns. It is not changed.
    """

    def __init__(self, client: IClient, structure: Table) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Table:
        """Table to read the columns of."""
        return self.__structure

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> Table:
        table: Table = super().execute(param_tuple)
        return table
