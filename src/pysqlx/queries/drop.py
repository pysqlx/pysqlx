"""Drop query."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..structures import Structure
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Drop(Query):
    """Query which drops a database, a schema or a table.

    :param client: the client which executes the query
    :param structure: the structure to drop
    """

    def __init__(self, client: IClient, structure: Structure) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Structure:
        """Structure to drop."""
        return self.__structure
