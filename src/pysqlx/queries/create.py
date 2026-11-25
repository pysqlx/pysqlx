"""Create query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Structure
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Create(Query):
    """Query which creates a database, a schema, a table or an index.

    :param client: the client which executes the query
    :param structure: the structure to create
    """

    def __init__(self, client: IClient, structure: Structure) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Structure:
        """Structure to create."""
        return self.__structure

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> None:
        super().execute(param_tuple)
