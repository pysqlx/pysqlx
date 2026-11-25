"""Conjunction of two clauses."""

from typing import override

from ....exceptions import InvalidArgumentError
from .clause import Clause


class And(Clause):
    """Clause which holds when both of two clauses hold.

    :param clause0: the first clause
    :param clause1: the second clause
    :raises InvalidArgumentError: if one of the arguments is not a clause
    """

    def __init__(self, clause0: Clause, clause1: Clause) -> None:
        if not all(
            (
                isinstance(clause0, Clause),
                isinstance(clause1, Clause),
            )
        ):
            raise InvalidArgumentError(
                f'invalid clauses of types "{type(clause0).__name__}" '
                f'and "{type(clause1).__name__}"'
            )

        super().__init__()

        self.__clause0 = clause0
        self.__clause1 = clause1

    @property
    def clause0(self) -> Clause:
        """First clause."""
        return self.__clause0

    @property
    def clause1(self) -> Clause:
        """Second clause."""
        return self.__clause1

    @override
    def get_not_clause(self) -> Clause:
        from .or_ import Or

        return Or(
            clause0=self.__clause0.get_not_clause(),
            clause1=self.__clause1.get_not_clause(),
        )
