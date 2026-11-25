"""Existence query."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..structures import Structure
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class IsExists(Query):
    """Query which checks whether a database, a schema or a table exists.

    :param client: the client which executes the query
    :param structure: the structure to look for
    """

    def __init__(self, client: IClient, structure: Structure) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Structure:
        """Structure to look for."""
        return self.__structure
