# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Logging for PyPtP - silent by default.

PyPtP follows Python library best practices by being silent by default.
Call configure_logging() explicitly to enable logging output.

Examples:
    >>> from pyptp.ptp_log import logger
    >>> logger.info("This will not appear (silent by default)")

    >>> from pyptp import configure_logging
    >>> configure_logging(level="DEBUG")
    >>> logger.debug("Now logging is enabled!")

    >>> # Log to file
    >>> configure_logging(sink="pyptp.log", level="INFO", colorize=False)

"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from logging import Handler
    from os import PathLike
    from typing import TextIO

    from loguru import Message

    # Type alias for loguru sink parameter
    LogSink = str | PathLike[str] | TextIO | Callable[[Message], None] | Handler

logger.remove()


def configure_logging(
    level: str = "INFO",
    sink: LogSink = sys.stderr,
    *,
    colorize: bool = True,
    format_string: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    **kwargs: Any,  # noqa: ANN401
) -> int:
    """Configure PyPtP logging.

    PyPtP is silent by default. Call this function explicitly to enable logging.

    Args:
        level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        sink: Output destination (sys.stderr, sys.stdout, file path, or file object).
        colorize: Enable colored output (auto-detects terminal support).
        format_string: Log message format string (loguru format).
        **kwargs: Additional arguments passed to loguru's logger.add().

    Returns:
        Handler ID (can be used with logger.remove(handler_id)).

    Examples:
        >>> import pyptp
        >>> # Enable console logging
        >>> pyptp.configure_logging(level="DEBUG")

        >>> # Log to file without colors
        >>> pyptp.configure_logging(
        ...     sink="pyptp.log",
        ...     level="INFO",
        ...     colorize=False,
        ...     rotation="10 MB"  # loguru feature
        ... )

        >>> # Multiple outputs
        >>> pyptp.configure_logging(sink=sys.stderr, level="WARNING")
        >>> pyptp.configure_logging(sink="app.log", level="DEBUG", colorize=False)

    """
    return logger.add(
        sink,
        level=level.upper(),
        colorize=colorize,
        format=format_string,
        **kwargs,
    )


__all__ = ["configure_logging", "logger"]
