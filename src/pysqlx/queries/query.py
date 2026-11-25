"""Base class of the queries."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..clients.i_client import IClient


class Query:
    """Base class of the queries.

    A query is created by a client and holds what to do. Nothing is sent to
    the database before :py:meth:`execute` or :py:meth:`execute_many` is
    called.

    :param client: the client which executes the query
    """

    def __init__(self, client: IClient) -> None:
        self.__client = client

    def execute(self, param_tuple: Sequence[Any] | None = None) -> Any:
        """Execute the query once.

        :param param_tuple: the values of the parameters of the query, for
            the queries which take parameters
        :returns: the result of the query, which depends on its type
        """
        return self.__client.execute(query=self, param_tuple=param_tuple)

    def execute_many(self, param_tuple_list: Sequence[Sequence[Any]]) -> Any:
        """Execute the query once for each set of parameter values.

        :param param_tuple_list: one sequence of parameter values per
            execution
        :returns: the result of the query, which depends on its type
        :raises UnsupportedOperationError: if the query does not support it
        """
        return self.__client.execute_many(query=self, param_tuple_list=param_tuple_list)
