"""Logger of the package."""

import logging

logger = logging.getLogger("pysqlx")
"""Logger which receives the executed SQL statements and their timings."""

# A library stays silent unless the application configures logging.
logger.addHandler(logging.NullHandler())
