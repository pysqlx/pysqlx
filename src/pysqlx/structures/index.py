"""Index."""

from collections.abc import Sequence

from ..exceptions import InvalidArgumentError
from .columntypes import Column
from .structure import Structure
from .table import Table


class Index(Structure):
    """Index on columns of a table, which speeds up looking rows up.

    An index is created, dropped and looked for like a table.

    :param index_name: the name of the index
    :param table: the table to index
    :param columns: the columns to index, in order
    :param is_unique: whether the index rejects rows with the same values in
        the indexed columns
    :raises InvalidArgumentError: if the columns are empty or do not belong
        to the table
    """

    def __init__(
        self,
        index_name: str,
        table: Table,
        columns: Sequence[Column],
        is_unique: bool = False,
    ) -> None:
        super().__init__(structure_name="index")

        if len(columns) < 1:
            raise InvalidArgumentError("empty columns")

        for column in columns:
            if not any(column is col for col in table.columns):
                raise InvalidArgumentError("invalid columns")

        self.__index_name = index_name
        self.__table = table
        self.__columns = columns
        self.__is_unique = is_unique

    @property
    def index_name(self) -> str:
        """Name of the index."""
        return self.__index_name

    @property
    def table(self) -> Table:
        """Table which is indexed."""
        return self.__table

    @property
    def columns(self) -> Sequence[Column]:
        """Columns which are indexed."""
        return self.__columns

    @property
    def is_unique(self) -> bool:
        """Whether the index rejects rows with the same indexed values."""
        return self.__is_unique
