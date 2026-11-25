"""Wait until the SQL Server of the tests accepts connections.

SQL Server opens its port well before it accepts a login, so this connects
with the client of the package until it succeeds. The server is read from
the environment variable ``PYSQLX_TEST_MSSQL``, in the form
``user:password@host:port/database``. Run it with ``make sql-server-wait``.
"""

import os
import time
from urllib.parse import unquote, urlsplit

from pysqlx import ClientFactory
from pysqlx.exceptions import PysqlxError

VARIABLE = "PYSQLX_TEST_MSSQL"
TIMEOUT = 300.0
INTERVAL = 5.0


def main() -> None:
    """Connect until it works, or give up after the timeout."""
    value = os.environ.get(VARIABLE)

    if not value:
        raise SystemExit(f"{VARIABLE} is not set")

    server = urlsplit("//" + value)
    start = time.monotonic()

    while True:
        try:
            client = ClientFactory.get_sql_server_client(
                server_address=server.hostname or "",
                user_name=unquote(server.username or ""),
                user_pass=unquote(server.password or ""),
                server_port=server.port,
                database_name=server.path.lstrip("/") or None,
                connection_options={"TrustServerCertificate": "yes"},
            )
        except PysqlxError as error:
            elapsed = time.monotonic() - start

            if elapsed > TIMEOUT:
                cause = error.__cause__ or error
                raise SystemExit(
                    f"SQL Server did not accept a connection in {TIMEOUT:.0f} seconds: {cause}"
                ) from error

            print(f"waiting for SQL Server ({elapsed:.0f} seconds)", flush=True)
            time.sleep(INTERVAL)
        else:
            client.close()
            print(f"SQL Server is ready after {time.monotonic() - start:.0f} seconds")
            return


if __name__ == "__main__":
    main()
