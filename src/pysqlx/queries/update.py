"""Update query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, override

from ..exceptions import InvalidArgumentError
from ..structures import Clause, Column, Table
from .query import Query
from .utility import check_cols

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Update(Query):
    """Query which changes the rows of a table which satisfy a condition.

    The new values of the columns are given when the query is executed.

    :param client: the client which executes the query
    :param structure: the table to change rows of
    :param columns: the columns to change. All columns of the table by
        default.
    :param condition: the condition which the changed rows satisfy
    :raises InvalidArgumentError: if the columns are invalid
    """

    def __init__(
        self,
        client: IClient,
        structure: Table,
        columns: Sequence[Column] | None,
        condition: Clause,
    ) -> None:
        super().__init__(client=client)

        if not columns:
            columns = structure.columns

        if not check_cols(columns, structure.columns):
            raise InvalidArgumentError("invalid columns")

        self.__structure = structure
        self.__columns = columns
        self.__condition = condition

    @property
    def structure(self) -> Table:
        """Table to change rows of."""
        return self.__structure

    @property
    def columns(self) -> Sequence[Column]:
        """Columns to change."""
        return self.__columns

    @property
    def condition(self) -> Clause:
        """Condition which the changed rows satisfy."""
        return self.__condition

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> None:
        super().execute(param_tuple)

    @override
    def execute_many(self, param_tuple_list: Sequence[Sequence[Any]]) -> None:
        super().execute_many(param_tuple_list)
