"""Join of a table."""

from ..exceptions import InvalidArgumentError
from .columntypes import Clause
from .table import Table

_kinds = (
    "inner",
    "left",
    "right",
    "full",
)


class Join:
    """Table joined to the table of a select query.

    :param table: the table to join
    :param condition: the condition which relates the rows of the two tables,
        such as ``orders_customer_id == customers_id``
    :param kind: ``"inner"`` to keep the rows which have a match in both
        tables, ``"left"`` to keep all rows of the table of the query,
        ``"right"`` to keep all rows of the joined table, or ``"full"`` to
        keep all rows of both
    :raises InvalidArgumentError: if the kind is unknown
    """

    def __init__(self, table: Table, condition: Clause, kind: str = "inner") -> None:
        if kind not in _kinds:
            raise InvalidArgumentError(f'invalid join kind "{kind}"')

        self.__table = table
        self.__condition = condition
        self.__kind = kind

    @property
    def table(self) -> Table:
        """Table to join."""
        return self.__table

    @property
    def condition(self) -> Clause:
        """Condition which relates the rows of the two tables."""
        return self.__condition

    @property
    def kind(self) -> str:
        """Kind of the join."""
        return self.__kind
