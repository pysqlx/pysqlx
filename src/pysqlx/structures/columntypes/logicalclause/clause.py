"""Base class of the logical clauses."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Clause(ABC):
    """Base class of the logical clauses.

    Clauses are combined with ``&`` and ``|`` and negated with ``~``.
    """

    def __init__(self) -> None:
        super().__init__()

    def __and__(self, other: Clause) -> Clause:
        from .and_ import And

        return And(clause0=self, clause1=other)

    def __or__(self, other: Clause) -> Clause:
        from .or_ import Or

        return Or(clause0=self, clause1=other)

    def __invert__(self) -> Clause:
        return self.get_not_clause()

    @abstractmethod
    def get_not_clause(self) -> Clause:
        """Create the negation of the clause.

        :returns: a clause which holds exactly when this one does not
        """
