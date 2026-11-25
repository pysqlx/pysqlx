"""Row count query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.client import Client


class CountRows(Query):
    """Query which counts the rows of a table.

    :param client: the client which executes the query
    :param table: the table to count the rows of
    """

    def __init__(self, client: Client, table: Table) -> None:
        super().__init__(client=client)

        self.__table = table

    @property
    def table(self) -> Table:
        """Table to count the rows of."""
        return self.__table

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> int:
        result: int = super().execute(parameters)
        return result
