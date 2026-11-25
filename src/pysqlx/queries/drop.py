"""Drop query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Structure
from .query import Query

if TYPE_CHECKING:
    from ..clients.client import Client


class Drop(Query):
    """Query which drops a database, a schema, a table or an index.

    :param client: the client which executes the query
    :param structure: the structure to drop
    """

    def __init__(self, client: Client, structure: Structure) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Structure:
        """Structure to drop."""
        return self.__structure

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> None:
        super().execute(parameters)
