"""In list clause."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, override

from .clause import Clause

if TYPE_CHECKING:
    from ..column import Column


class InList(Clause):
    """Clause which holds when a column is one of a list of values.

    :param column: the column to test
    :param val_list: the values to compare the column with
    """

    def __init__(self, column: Column, val_list: Iterable[Any]) -> None:
        super().__init__()

        self.__column = column
        self.__val_list = val_list

    @property
    def column(self) -> Column:
        """Column to test."""
        return self.__column

    @property
    def val_list(self) -> Iterable[Any]:
        """Values to compare the column with."""
        return self.__val_list

    @override
    def get_not_clause(self) -> Clause:
        from .not_in_list import NotInList

        return NotInList(column=self.__column, val_list=self.__val_list)
