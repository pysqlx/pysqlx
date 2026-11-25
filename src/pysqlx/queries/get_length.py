"""Row count query."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class GetLength(Query):
    """Query which counts the rows of a table.

    :param client: the client which executes the query
    :param structure: the table to count the rows of
    """

    def __init__(self, client: IClient, structure: Table) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Table:
        """Table to count the rows of."""
        return self.__structure
