"""Schema."""

from .structure import Structure


class Schema(Structure):
    """Schema of a database.

    :param schema_name: the name of the schema
    :param owner_name: the name of the owner of the schema, if any
    """

    def __init__(self, schema_name: str, owner_name: str | None = None) -> None:
        super().__init__(structure_name="schema")

        self.__schema_name = schema_name
        self.__owner_name = owner_name

    @property
    def schema_name(self) -> str:
        """Name of the schema."""
        return self.__schema_name

    @property
    def owner_name(self) -> str | None:
        """Name of the owner of the schema, or ``None``."""
        return self.__owner_name
