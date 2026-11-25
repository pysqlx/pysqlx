"""Base class of the exceptions."""


class PysqlxError(RuntimeError):
    """Base class of the exceptions raised by the package.

    It derives from ``RuntimeError``, which the package raised before it had
    exceptions of its own.
    """
