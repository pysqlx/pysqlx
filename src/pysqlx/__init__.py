"""A generic SQL driver package."""

from importlib.metadata import version

from .clients import ClientFactory
from .structures import Database, Schema, Table

__version__ = version("pysqlx")

__all__ = [
    "__version__",
    "ClientFactory",
    "Database",
    "Schema",
    "Table",
]
