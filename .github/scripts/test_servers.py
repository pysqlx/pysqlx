"""Start and stop the throwaway database servers which the tests of the clients use.

The servers run as Docker containers. Run it with ``make servers-up``,
``make servers-down`` and ``make sql-server-up``, or directly::

    python .github/scripts/test_servers.py up
    python .github/scripts/test_servers.py up --servers sql-server --colima
    python .github/scripts/test_servers.py down

``--colima`` installs and starts Colima on macOS when Docker is not running,
which is how the workflows get Docker on a macOS runner.

The addresses to give to the tests, as the environment variables which
``tests/conftest.py`` reads, are printed after the servers are started.
"""

import argparse
import platform
import shutil
import subprocess
from dataclasses import dataclass

PASSWORD = "pysqlx_test"
SQL_SERVER_PASSWORD = "Pysqlx_test_1"


@dataclass(frozen=True)
class Server:
    """A database server which runs in a container.

    :param container: the name of the container
    :param image: the image to run
    :param port: the port of the server inside the container
    :param host_port: the port which reaches the server from this machine
    :param environment: the environment variables which set the server up
    :param variable: the environment variable which gives the server to the tests
    :param address: the value of that variable
    """

    container: str
    image: str
    port: int
    host_port: int
    environment: dict[str, str]
    variable: str
    address: str


SERVERS = {
    "postgresql": Server(
        container="pysqlx-test-postgres",
        image="postgres:17",
        port=5432,
        host_port=55432,
        environment={"POSTGRES_PASSWORD": PASSWORD},
        variable="PYSQLX_TEST_POSTGRESQL",
        address=f"postgres:{PASSWORD}@127.0.0.1:55432/postgres",
    ),
    "mysql": Server(
        container="pysqlx-test-mysql",
        image="mysql:8.4",
        port=3306,
        host_port=53306,
        environment={"MYSQL_ROOT_PASSWORD": PASSWORD, "MYSQL_DATABASE": "pysqlx"},
        variable="PYSQLX_TEST_MYSQL",
        address=f"root:{PASSWORD}@127.0.0.1:53306/pysqlx",
    ),
    "sql-server": Server(
        container="pysqlx-test-sql-server",
        image="mcr.microsoft.com/mssql/server:2022-latest",
        port=1433,
        host_port=1433,
        environment={"ACCEPT_EULA": "Y", "MSSQL_SA_PASSWORD": SQL_SERVER_PASSWORD},
        variable="PYSQLX_TEST_MSSQL",
        address=f"sa:{SQL_SERVER_PASSWORD}@127.0.0.1:1433/master",
    ),
}

DEFAULT_SERVERS = ("postgresql", "mysql")


def run(*command: str, check: bool = True) -> int:
    """Run a command, and show it first."""
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, check=check).returncode


def is_docker_running() -> bool:
    """Check whether Docker can be used."""
    if shutil.which("docker") is None:
        return False

    return subprocess.run(["docker", "info"], check=False, capture_output=True).returncode == 0


def start_colima() -> None:
    """Install and start Colima, which runs Docker on macOS."""
    if platform.system() != "Darwin":
        raise SystemExit("--colima is for macOS; start Docker yourself on this system")

    run("brew", "install", "docker", "colima")
    run("colima", "start", "--cpu", "2", "--memory", "4")


def up(names: list[str], colima: bool) -> None:
    """Start the servers."""
    if not is_docker_running():
        if not colima:
            raise SystemExit("Docker is not running; start it, or pass --colima on macOS")

        start_colima()

    for name in names:
        server = SERVERS[name]

        command = ["docker", "run", "-d", "--rm", "--name", server.container]

        for key, value in server.environment.items():
            command += ["-e", f"{key}={value}"]

        command += ["-p", f"{server.host_port}:{server.port}", server.image]

        run(*command)

    print("\nGive the servers to the tests with:")

    for name in names:
        print(f"  export {SERVERS[name].variable}={SERVERS[name].address}")


def down(names: list[str]) -> None:
    """Stop the servers, which removes their containers."""
    for name in names:
        run("docker", "stop", SERVERS[name].container, check=False)


def main() -> None:
    """Read the command line and act on it."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("up", "down"))
    parser.add_argument(
        "--servers",
        nargs="+",
        choices=tuple(SERVERS),
        default=None,
        help="the servers to act on (up: postgresql and mysql; down: all)",
    )
    parser.add_argument(
        "--colima",
        action="store_true",
        help="on macOS, install and start Colima when Docker is not running",
    )
    arguments = parser.parse_args()

    if arguments.command == "up":
        up(arguments.servers or list(DEFAULT_SERVERS), arguments.colima)
    else:
        down(arguments.servers or list(SERVERS))


if __name__ == "__main__":
    main()
