"""Delete query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, override

from ..structures import Clause, Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Delete(Query):
    """Query which removes the rows of a table which satisfy a condition.

    :param client: the client which executes the query
    :param structure: the table to remove rows from
    :param condition: the condition which the removed rows satisfy
    """

    def __init__(self, client: IClient, structure: Table, condition: Clause) -> None:
        super().__init__(client=client)

        self.__structure = structure
        self.__condition = condition

    @property
    def structure(self) -> Table:
        """Table to remove rows from."""
        return self.__structure

    @property
    def condition(self) -> Clause:
        """Condition which the removed rows satisfy."""
        return self.__condition

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> None:
        super().execute(param_tuple)
