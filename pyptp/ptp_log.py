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

import logging
import sys
from os import PathLike
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TextIO

    LogSink = str | PathLike[str] | TextIO | Callable[[str], None] | logging.Handler

logger = logging.getLogger("pyptp")
logger.addHandler(logging.NullHandler())

DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

_handler_counter = 0
_handlers: dict[int, logging.Handler] = {}

# ANSI color codes
_RESET = "\033[0m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_BLUE = "\033[34m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD_RED = "\033[1;31m"

_LEVEL_COLORS: dict[int, str] = {
    logging.DEBUG: _BLUE,
    logging.INFO: _GREEN,
    logging.WARNING: _YELLOW,
    logging.ERROR: _RED,
    logging.CRITICAL: _BOLD_RED,
}


class _ColorFormatter(logging.Formatter):
    """Formatter that adds ANSI color codes matching loguru's color scheme."""

    def format(self, record: logging.LogRecord) -> str:
        level_color = _LEVEL_COLORS.get(record.levelno, "")
        record = logging.makeLogRecord(record.__dict__)
        timestamp = f"{_GREEN}{self.formatTime(record, self.datefmt)}{_RESET}"
        levelname = f"{level_color}{record.levelname:<8}{_RESET}"
        name = f"{_CYAN}{record.name}{_RESET}"
        func = f"{_CYAN}{record.funcName}{_RESET}"
        lineno = f"{_CYAN}{record.lineno}{_RESET}"
        msg = record.getMessage()
        return f"{timestamp} | {levelname} | {name}:{func}:{lineno} - {level_color}{msg}{_RESET}"


class _CallableHandler(logging.Handler):
    """Handler that delegates to a callable sink."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self._callback(msg)


def configure_logging(
    level: str = "INFO",
    sink: LogSink = sys.stderr,
    *,
    colorize: bool = True,
    format_string: str = DEFAULT_FORMAT,
    **kwargs: Any,  # noqa: ANN401
) -> int:
    """Configure PyPtP logging.

    PyPtP is silent by default. Call this function explicitly to enable logging.

    Args:
        level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        sink: Output destination (sys.stderr, sys.stdout, file path, or file object).
        colorize: Enable colored output (auto-detects terminal support).
        format_string: Log message format string (stdlib logging format).
        **kwargs: Additional arguments passed to the handler constructor
            (e.g., ``encoding`` and ``mode`` for file handlers).

    Returns:
        Handler ID (can be used with logger.removeHandler via _handlers dict).

    Examples:
        >>> import pyptp
        >>> # Enable console logging
        >>> pyptp.configure_logging(level="DEBUG")

        >>> # Log to file without colors
        >>> pyptp.configure_logging(
        ...     sink="pyptp.log",
        ...     level="INFO",
        ...     colorize=False,
        ... )

        >>> # Multiple outputs
        >>> pyptp.configure_logging(sink=sys.stderr, level="WARNING")
        >>> pyptp.configure_logging(sink="app.log", level="DEBUG", colorize=False)

    """
    global _handler_counter  # noqa: PLW0603

    handler: logging.Handler
    is_stream = False

    if isinstance(sink, logging.Handler):
        handler = sink
    elif isinstance(sink, (str, PathLike)):
        handler = logging.FileHandler(str(sink), **kwargs)
        kwargs = {}
    elif hasattr(sink, "write"):
        handler = logging.StreamHandler(sink)  # type: ignore[arg-type]
        is_stream = True
    elif callable(sink):
        handler = _CallableHandler(sink)
    else:
        msg = f"Unsupported sink type: {type(sink)}"
        raise TypeError(msg)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handler.setLevel(numeric_level)

    use_color = colorize and is_stream and _stream_is_tty(handler)
    if use_color:
        formatter = _ColorFormatter(format_string, datefmt=DEFAULT_DATEFMT)
    else:
        formatter = logging.Formatter(format_string, datefmt=DEFAULT_DATEFMT)
    handler.setFormatter(formatter)

    if logger.level == logging.NOTSET or logger.level > numeric_level:
        logger.setLevel(numeric_level)

    logger.addHandler(handler)

    _handler_counter += 1
    _handlers[_handler_counter] = handler
    return _handler_counter


def _stream_is_tty(handler: logging.Handler) -> bool:
    """Check if a stream handler's stream is a TTY."""
    if not isinstance(handler, logging.StreamHandler):
        return False
    stream = handler.stream
    return hasattr(stream, "isatty") and stream.isatty()


__all__ = ["configure_logging", "logger"]
