"""A generic SQL driver package."""

from importlib.metadata import version

from .clients import ClientFactory
from .structures import Database, Index, Join, Schema, Table

__version__ = version("pysqlx")

__all__ = [
    "ClientFactory",
    "Database",
    "Index",
    "Join",
    "Schema",
    "Table",
    "__version__",
]
