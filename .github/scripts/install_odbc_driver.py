"""Install the ODBC driver for SQL Server, which the SQL Server client needs.

Run it with ``make odbc-driver``. It is used by the workflows, and works on a
development machine as well:

* Linux (Debian, Ubuntu): installs ``msodbcsql18`` with ``apt-get``
* macOS: installs ``msodbcsql18`` with Homebrew
* Windows: does nothing, as the driver comes with the system or with SQL Server
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path

DRIVER_NAME = "ODBC Driver 18 for SQL Server"
PACKAGE_NAME = "msodbcsql18"

KEY_URL = "https://packages.microsoft.com/keys/microsoft.asc"
KEY_PATH = "/usr/share/keyrings/microsoft-prod.gpg"
SOURCE_PATH = "/etc/apt/sources.list.d/mssql-release.list"
TAP_NAME = "microsoft/mssql-release"
TAP_URL = "https://github.com/Microsoft/homebrew-mssql-release"


def run(
    *command: str,
    check: bool = True,
    environment: dict[str, str] | None = None,
    text: str | None = None,
) -> int:
    """Run a command, and show it first.

    :param command: the program and its arguments
    :param check: whether to stop when the command fails
    :param environment: the environment variables of the command, if not
        those of this script
    :param text: what the command reads as its input, in which case its
        output is not shown
    :returns: the exit code of the command
    """
    print("+", " ".join(command), flush=True)

    return subprocess.run(
        command,
        check=check,
        env=environment,
        input=text,
        stdout=subprocess.DEVNULL if text is not None else None,
        text=True,
    ).returncode


def is_installed() -> bool:
    """Check whether unixODBC already knows the driver."""
    if shutil.which("odbcinst") is None:
        return False

    result = subprocess.run(["odbcinst", "-q", "-d"], check=False, capture_output=True, text=True)

    return DRIVER_NAME in result.stdout


def install_with_apt() -> bool:
    """Install the driver from the package sources which the system knows."""
    environment = "ACCEPT_EULA=Y"

    return (
        run("sudo", "apt-get", "update", check=False) == 0
        and run("sudo", environment, "apt-get", "install", "-y", PACKAGE_NAME, check=False) == 0
    )


def add_apt_source() -> None:
    """Add the package source of Microsoft for this version of the system."""
    release = subprocess.run(
        ["lsb_release", "-rs"], check=True, capture_output=True, text=True
    ).stdout.strip()
    codename = subprocess.run(
        ["lsb_release", "-cs"], check=True, capture_output=True, text=True
    ).stdout.strip()
    distribution = (
        subprocess.run(["lsb_release", "-is"], check=True, capture_output=True, text=True)
        .stdout.strip()
        .lower()
    )

    key = subprocess.run(["curl", "-fsSL", KEY_URL], check=True, capture_output=True).stdout

    # gpg asks on a terminal before it replaces a file, unless it runs in batch mode.
    subprocess.run(
        ["sudo", "gpg", "--batch", "--yes", "--dearmor", "-o", KEY_PATH], check=True, input=key
    )

    architecture = "arm64" if platform.machine() in ("aarch64", "arm64") else "amd64"
    source = (
        f"deb [arch={architecture} signed-by={KEY_PATH}] "
        f"https://packages.microsoft.com/{distribution}/{release}/prod {codename} main\n"
    )

    run("sudo", "tee", SOURCE_PATH, text=source)


def install_on_linux() -> None:
    """Install the driver on Debian or Ubuntu."""
    # A hosted runner usually knows the package source of Microsoft already.
    if install_with_apt():
        return

    add_apt_source()

    if not install_with_apt():
        raise SystemExit(f"could not install {PACKAGE_NAME}")


def install_on_macos() -> None:
    """Install the driver with Homebrew."""
    run("brew", "tap", TAP_NAME, TAP_URL)

    # Homebrew does not load formulae of a tap which was not trusted. Versions
    # of Homebrew without this command do not need it.
    run("brew", "trust", TAP_NAME, check=False)

    run("brew", "install", PACKAGE_NAME, environment={**os.environ, "HOMEBREW_ACCEPT_EULA": "Y"})


def main() -> None:
    """Install the driver unless it is there already."""
    system = platform.system()

    if system == "Windows":
        print("Windows: the ODBC driver comes with the system or with SQL Server")
        return

    if is_installed():
        print(f'"{DRIVER_NAME}" is already installed')
        return

    if system == "Linux":
        if not Path("/usr/bin/apt-get").exists():
            raise SystemExit("only Debian and Ubuntu are supported, install the driver by hand")

        install_on_linux()
    elif system == "Darwin":
        install_on_macos()
    else:
        raise SystemExit(f'unsupported system "{system}"')

    if not is_installed():
        raise SystemExit(f'"{DRIVER_NAME}" was installed but unixODBC does not list it')

    print(f'installed "{DRIVER_NAME}"')


if __name__ == "__main__":
    main()
