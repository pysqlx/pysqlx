"""Truncate query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, override

from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Truncate(Query):
    """Query which removes all rows of a table.

    :param client: the client which executes the query
    :param structure: the table to empty
    """

    def __init__(self, client: IClient, structure: Table) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Table:
        """Table to empty."""
        return self.__structure

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> None:
        super().execute(param_tuple)
