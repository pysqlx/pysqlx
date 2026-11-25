"""Emptiness query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class IsEmpty(Query):
    """Query which checks whether a table has no rows.

    :param client: the client which executes the query
    :param structure: the table to check
    """

    def __init__(self, client: IClient, structure: Table) -> None:
        super().__init__(client=client)

        self.__structure = structure

    @property
    def structure(self) -> Table:
        """Table to check."""
        return self.__structure

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> bool:
        result: bool = super().execute(param_tuple)
        return result
