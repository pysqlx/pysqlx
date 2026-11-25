"""Delete query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..structures import Clause, Table
from .query import Query

if TYPE_CHECKING:
    from ..clients.client import Client


class Delete(Query):
    """Query which removes the rows of a table which satisfy a condition.

    :param client: the client which executes the query
    :param table: the table to remove rows from
    :param condition: the condition which the removed rows satisfy
    """

    def __init__(self, client: Client, table: Table, condition: Clause) -> None:
        super().__init__(client=client)

        self.__table = table
        self.__condition = condition

    @property
    def table(self) -> Table:
        """Table to remove rows from."""
        return self.__table

    @property
    def condition(self) -> Clause:
        """Condition which the removed rows satisfy."""
        return self.__condition

    @override
    def execute(self, parameters: Sequence[Any] | None = None) -> None:
        super().execute(parameters)
