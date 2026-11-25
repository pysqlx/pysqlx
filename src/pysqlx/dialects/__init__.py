"""SQL dialects, which turn queries into SQL strings."""

from .i_dialect import IDialect
from .ms_sql import MsSql
from .my_sql import MySql
from .postgre_sql import PostgreSql
from .sqlite import Sqlite

__all__ = [
    "IDialect",
    "MsSql",
    "MySql",
    "PostgreSql",
    "Sqlite",
]
