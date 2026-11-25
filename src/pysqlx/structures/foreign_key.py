"""Foreign key."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..exceptions import InvalidArgumentError
from .columntypes import Column

if TYPE_CHECKING:
    from .table import Table


class ForeignKey:
    """Constraint which makes columns refer to the rows of another table.

    Foreign keys are created by ``Table.append_foreign_key()``.

    :param columns: the columns which refer to the other table
    :param reference_columns: the columns which they refer to, in the same
        order. All of them belong to the same table.
    :raises InvalidArgumentError: if the columns are empty, differ in number
        or the referenced columns belong to several tables
    """

    def __init__(
        self,
        columns: Sequence[Column],
        reference_columns: Sequence[Column],
    ) -> None:
        if len(columns) < 1:
            raise InvalidArgumentError("empty columns")

        if len(columns) != len(reference_columns):
            raise InvalidArgumentError("columns and reference_columns size mismatch")

        reference_table_name = reference_columns[0].table.table_name

        for column in reference_columns:
            if column.table.table_name != reference_table_name:
                raise InvalidArgumentError("reference_columns belong to several tables")

        self.__columns = columns
        self.__reference_columns = reference_columns
        # The columns only refer to their table weakly. Keep the table, so that
        # it lives as long as the foreign key which needs it.
        self.__reference_table = reference_columns[0].table._get_self()

    @property
    def columns(self) -> Sequence[Column]:
        """Columns which refer to the other table."""
        return self.__columns

    @property
    def reference_columns(self) -> Sequence[Column]:
        """Columns which are referred to."""
        return self.__reference_columns

    @property
    def reference_table(self) -> Table:
        """Table which is referred to."""
        return self.__reference_table
