import importlib
import os
import warnings
from pkgutil import walk_packages

import pytest

_dir = os.path.abspath(os.path.dirname(__file__))

ALL_PACKAGES = ["pysqlx"]

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        _dir,
        "..",
    )
)


def all_modules() -> tuple[str, ...]:

    def onerror(name: str) -> None:
        warnings.warn(
            f"Failed to import {name} when expanding module_info fixture",
            stacklevel=2,
        )

    modules = [
        w
        for p in ALL_PACKAGES
        for w in walk_packages(
            [os.path.join(PROJECT_ROOT, "src", p)],
            prefix=f"{p}.",
            onerror=onerror,
        )
    ]

    return tuple(m.name for m in modules)


@pytest.mark.parametrize("module_name", all_modules())
def test_loads(module_name: str) -> None:
    importlib.import_module(module_name)
