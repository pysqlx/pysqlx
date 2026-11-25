"""Reflect query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.client import Client


class Reflect(Query):
    """Query which reads the columns of a table from the database.

    The result is a table with the columns found in the database, to use in
    other queries. Its foreign keys are read as well, with the columns of the
    tables they refer to.

    :param client: the client which executes the query
    :param table: the table to read the columns of, given without
        columns. It is not changed.
    """

    def __init__(self, client: Client, table: Table) -> None:
        super().__init__(client=client)

        self.__table = table

    @property
    def table(self) -> Table:
        """Table to read the columns of."""
        return self.__table

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> Table:
        table: Table = super().execute(parameters)
        return table
