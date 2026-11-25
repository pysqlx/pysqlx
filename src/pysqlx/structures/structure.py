"""Base class of the database structures."""


class Structure:
    """Base class of the database structures.

    :param structure_name: the kind of the structure, such as ``"table"``
    """

    def __init__(self, structure_name: str) -> None:
        self.__structure_name = structure_name

    @property
    def structure_name(self) -> str:
        """Kind of the structure, which selects the SQL to generate."""
        return self.__structure_name
