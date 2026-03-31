# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for pyptp.ptp_log — stdlib logging backend."""

from __future__ import annotations

import io
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from pyptp.ptp_log import (
    _CallableHandler,
    _ColorFormatter,
    _handlers,
    _stream_is_tty,
    configure_logging,
    logger,
)


class _LogTestCase(unittest.TestCase):
    """Base that resets the pyptp logger between tests."""

    def setUp(self) -> None:
        self._original_handlers = logger.handlers[:]
        self._original_level = logger.level

    def tearDown(self) -> None:
        for h in logger.handlers[:]:
            if h not in self._original_handlers:
                logger.removeHandler(h)
                h.close()
        logger.setLevel(self._original_level)
        _handlers.clear()


class TestSilentByDefault(_LogTestCase):
    """Logger must produce no output unless explicitly configured."""

    def test_default_handler_is_null(self):
        fresh = logging.getLogger("pyptp")
        has_null = any(isinstance(h, logging.NullHandler) for h in fresh.handlers)
        self.assertTrue(has_null)

    def test_no_configured_handlers(self):
        """Without configure_logging, only the NullHandler is present."""
        pyptp_handlers = [
            h for h in logger.handlers if not isinstance(h, logging.NullHandler)
        ]
        self.assertEqual(pyptp_handlers, [])


class TestConfigureLogging(_LogTestCase):
    """Test configure_logging() with various sink types."""

    def test_stream_sink(self):
        buf = io.StringIO()
        handler_id = configure_logging(level="DEBUG", sink=buf, colorize=False)
        self.assertIsInstance(handler_id, int)
        logger.info("hello %s", "world")
        output = buf.getvalue()
        self.assertIn("hello world", output)

    def test_format_string_substitution(self):
        """The core bug fix: %s placeholders must be substituted."""
        buf = io.StringIO()
        configure_logging(level="DEBUG", sink=buf, colorize=False)
        logger.debug("value=%s count=%d", "abc", 42)
        output = buf.getvalue()
        self.assertIn("value=abc", output)
        self.assertIn("count=42", output)
        self.assertNotIn("%s", output)
        self.assertNotIn("%d", output)

    def test_repr_formatting(self):
        buf = io.StringIO()
        configure_logging(level="DEBUG", sink=buf, colorize=False)
        logger.debug("obj=%r", "test")
        output = buf.getvalue()
        self.assertIn("obj='test'", output)

    def test_file_sink(self):
        tmpdir = tempfile.mkdtemp()
        log_path = Path(tmpdir) / "test.log"
        hid = configure_logging(level="INFO", sink=str(log_path), colorize=False)
        logger.info("file test %s", "ok")
        handler = _handlers[hid]
        handler.flush()
        handler.close()
        logger.removeHandler(handler)
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("file test ok", content)

    def test_pathlike_sink(self):
        tmpdir = tempfile.mkdtemp()
        log_path = Path(tmpdir) / "test2.log"
        hid = configure_logging(level="INFO", sink=log_path, colorize=False)
        logger.info("pathlike test")
        handler = _handlers[hid]
        handler.flush()
        handler.close()
        logger.removeHandler(handler)
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("pathlike test", content)

    def test_callable_sink(self):
        messages: list[str] = []
        configure_logging(level="INFO", sink=messages.append, colorize=False)
        logger.info("callback %s", "test")
        self.assertEqual(len(messages), 1)
        self.assertIn("callback test", messages[0])

    def test_handler_sink(self):
        buf = io.StringIO()
        raw_handler = logging.StreamHandler(buf)
        configure_logging(level="DEBUG", sink=raw_handler, colorize=False)
        logger.debug("direct handler")
        self.assertIn("direct handler", buf.getvalue())

    def test_unsupported_sink_raises(self):
        with self.assertRaises(TypeError):
            configure_logging(sink=12345)  # type: ignore[arg-type]

    def test_returns_incrementing_ids(self):
        buf = io.StringIO()
        id1 = configure_logging(level="INFO", sink=buf, colorize=False)
        id2 = configure_logging(level="INFO", sink=buf, colorize=False)
        self.assertIsInstance(id1, int)
        self.assertIsInstance(id2, int)
        self.assertEqual(id2, id1 + 1)

    def test_handler_tracked_in_dict(self):
        buf = io.StringIO()
        hid = configure_logging(level="INFO", sink=buf, colorize=False)
        self.assertIn(hid, _handlers)
        self.assertIsInstance(_handlers[hid], logging.Handler)

    def test_multiple_sinks(self):
        buf1 = io.StringIO()
        buf2 = io.StringIO()
        configure_logging(level="INFO", sink=buf1, colorize=False)
        configure_logging(level="INFO", sink=buf2, colorize=False)
        logger.info("multi-sink %s", "test")
        self.assertIn("multi-sink test", buf1.getvalue())
        self.assertIn("multi-sink test", buf2.getvalue())

    def test_level_filtering(self):
        buf = io.StringIO()
        configure_logging(level="WARNING", sink=buf, colorize=False)
        logger.debug("should not appear")
        logger.info("should not appear either")
        logger.warning("should appear")
        output = buf.getvalue()
        self.assertNotIn("should not appear", output)
        self.assertIn("should appear", output)

    def test_logger_level_lowered_for_more_permissive_handler(self):
        buf = io.StringIO()
        configure_logging(level="WARNING", sink=buf, colorize=False)
        level_after_warning = logger.level
        configure_logging(level="DEBUG", sink=buf, colorize=False)
        level_after_debug = logger.level
        self.assertLessEqual(level_after_debug, level_after_warning)

    def test_custom_format_string(self):
        buf = io.StringIO()
        configure_logging(
            level="INFO",
            sink=buf,
            colorize=False,
            format_string="[%(levelname)s] %(message)s",
        )
        logger.info("custom format")
        self.assertIn("[INFO] custom format", buf.getvalue())

    def test_exception_logging(self):
        buf = io.StringIO()
        configure_logging(level="ERROR", sink=buf, colorize=False)
        try:
            raise ValueError("test error")  # noqa: TRY301
        except ValueError:
            logger.exception("caught")
        output = buf.getvalue()
        self.assertIn("caught", output)
        self.assertIn("ValueError: test error", output)


class TestColorFormatter(_LogTestCase):
    """Test _ColorFormatter ANSI output."""

    def test_output_contains_ansi_codes(self):
        formatter = _ColorFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        record = logging.LogRecord(
            name="pyptp",
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg="test %s",
            args=("value",),
            exc_info=None,
        )
        output = formatter.format(record)
        self.assertIn("\033[", output)  # Contains ANSI escape
        self.assertIn("test value", output)
        self.assertIn("\033[0m", output)  # Contains reset

    def test_color_does_not_corrupt_message(self):
        formatter = _ColorFormatter("%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        record = logging.LogRecord(
            name="pyptp",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="plain text",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        self.assertIn("plain text", output)


class TestCallableHandler(unittest.TestCase):
    """Test _CallableHandler."""

    def test_calls_callback(self):
        callback = MagicMock()
        handler = _CallableHandler(callback)
        handler.setFormatter(logging.Formatter("%(message)s"))
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        callback.assert_called_once_with("hello")


class TestStreamIsTty(unittest.TestCase):
    """Test _stream_is_tty helper."""

    def test_non_stream_handler_returns_false(self):
        handler = logging.NullHandler()
        self.assertFalse(_stream_is_tty(handler))

    def test_stringio_returns_false(self):
        handler = logging.StreamHandler(io.StringIO())
        self.assertFalse(_stream_is_tty(handler))

    def test_mock_tty_returns_true(self):
        stream = MagicMock()
        stream.isatty.return_value = True
        handler = logging.StreamHandler(stream)
        self.assertTrue(_stream_is_tty(handler))


if __name__ == "__main__":
    unittest.main()
