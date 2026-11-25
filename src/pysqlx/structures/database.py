"""Database."""

from .structure import Structure


class Database(Structure):
    """Database on a server.

    :param database_name: the name of the database
    """

    def __init__(self, database_name: str) -> None:
        super().__init__(structure_name="database")

        self.__database_name = database_name

    @property
    def database_name(self) -> str:
        """Name of the database."""
        return self.__database_name
