"""SQL dialects, which turn queries into SQL strings."""

from .i_dialect import IDialect
from .ms_sql import MsSql
from .sqlite import Sqlite

__all__ = [
    "IDialect",
    "MsSql",
    "Sqlite",
]
