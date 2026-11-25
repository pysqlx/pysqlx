"""Not like clause."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...._compat import override
from .clause import Clause

if TYPE_CHECKING:
    from ..column import Column


class NotLike(Clause):
    """Clause which holds when a column does not match a pattern.

    :param column: the column to test
    :param value: the pattern, in which ``%`` stands for any sequence of
        characters and ``_`` for any single character
    """

    def __init__(self, column: Column, value: Any) -> None:
        super().__init__()

        self.__column = column
        self.__value = value

    @property
    def column(self) -> Column:
        """Column to test."""
        return self.__column

    @property
    def value(self) -> Any:
        """Pattern to match."""
        return self.__value

    @override
    def get_not_clause(self) -> Clause:
        from .like import Like

        return Like(column=self.column, value=self.value)
