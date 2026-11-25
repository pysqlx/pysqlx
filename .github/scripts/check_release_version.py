"""Check that the built distributions have the version of a release tag.

The version of the package is read from the git tags when it is built. This
makes sure that what is about to be published is the release which was
tagged: for the tag ``v2.1.0``, ``dist`` must hold ``pysqlx-2.1.0.tar.gz``
and ``pysqlx-2.1.0-py3-none-any.whl``. Run it with
``make check-version TAG=v2.1.0``.
"""

import sys
from pathlib import Path

PACKAGE_NAME = "pysqlx"
DIST_DIR = Path(__file__).parent.parent.parent / "dist"


def main() -> None:
    """Compare the files of ``dist`` with the tag given on the command line."""
    if len(sys.argv) != 2 or not sys.argv[1]:
        raise SystemExit("usage: check_release_version.py TAG")

    version = sys.argv[1].removeprefix("v")
    expected = [
        f"{PACKAGE_NAME}-{version}.tar.gz",
        f"{PACKAGE_NAME}-{version}-py3-none-any.whl",
    ]
    found = sorted(path.name for path in DIST_DIR.glob("*")) if DIST_DIR.is_dir() else []

    print("built:", ", ".join(found) or "nothing")

    missing = [name for name in expected if name not in found]

    if missing:
        raise SystemExit(f"the version does not match the tag: missing {', '.join(missing)}")

    print(f"the distributions match the tag {sys.argv[1]}")


if __name__ == "__main__":
    main()
