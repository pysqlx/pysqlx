"""Names which are not available in every supported version of Python."""

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING or sys.version_info >= (3, 12):
    from typing import override
else:

    def override(method: Callable[..., Any]) -> Callable[..., Any]:
        """Mark a method which overrides a method of a base class."""
        return method


__all__ = [
    "override",
]
