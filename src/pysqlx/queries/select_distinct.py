"""Select distinct query."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._compat import override
from ..exceptions import InvalidArgumentError
from ..structures import Clause, Column, Table
from .query import Query
from .utility import check_cols, check_order_by_cols

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class SelectDistinct(Query):
    """Query which reads the distinct values of columns of a table.

    :param client: the client which executes the query
    :param structure: the table to read from
    :param columns: the columns to read
    :param ascend_by: the columns to sort by in ascending order
    :param descend_by: the columns to sort by in descending order
    :param condition: the condition which the rows satisfy
    :raises InvalidArgumentError: if an argument is invalid
    """

    def __init__(
        self,
        client: IClient,
        structure: Table,
        columns: Sequence[Column],
        ascend_by: Sequence[Column] | None,
        descend_by: Sequence[Column] | None,
        condition: Clause | None,
    ) -> None:
        super().__init__(client=client)

        if len(columns) < 1:
            raise InvalidArgumentError("empty columns")

        if not check_cols(columns, structure.columns):
            raise InvalidArgumentError("invalid columns")

        if ascend_by and not check_cols(ascend_by, columns):
            raise InvalidArgumentError("invalid ascend_by")

        if descend_by and not check_cols(descend_by, columns):
            raise InvalidArgumentError("invalid descend_by")

        if not check_order_by_cols(ascend_by, descend_by):
            raise InvalidArgumentError("invalid ascend_by and descend_by")

        self.__structure = structure
        self.__columns = columns
        self.__ascend_by = ascend_by
        self.__descend_by = descend_by
        self.__condition = condition

    @property
    def structure(self) -> Table:
        """Table to read from."""
        return self.__structure

    @property
    def columns(self) -> Sequence[Column]:
        """Columns to read."""
        return self.__columns

    @property
    def ascend_by(self) -> Sequence[Column] | None:
        """Columns to sort by in ascending order, or ``None``."""
        return self.__ascend_by

    @property
    def descend_by(self) -> Sequence[Column] | None:
        """Columns to sort by in descending order, or ``None``."""
        return self.__descend_by

    @property
    def condition(self) -> Clause | None:
        """Condition which the rows satisfy, or ``None``."""
        return self.__condition

    @override
    def execute(self, param_tuple: Sequence[Any] | None = None) -> tuple[tuple[Any, ...], ...]:
        rows: tuple[tuple[Any, ...], ...] = super().execute(param_tuple)
        return rows
