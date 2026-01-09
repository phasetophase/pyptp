"""Serialization helper function validation test suite.

Tests format string generation functions used throughout the PyPtP library
for consistent GNF/VNF property serialization.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch
from uuid import UUID

from pyptp.elements.color_utils import CL_RED
from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.serialization_helpers import (
    sanitize_quoted_string,
    write_boolean,
    write_boolean_no_skip,
    write_color,
    write_color_no_skip,
    write_delphi_color,
    write_double,
    write_double_no_skip,
    write_float_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
    write_string_no_skip,
)


class TestSerializationHelpers(unittest.TestCase):
    """Validation tests for GNF/VNF property serialization functions.

    Ensures consistent format string generation across all element types
    with proper handling of default values, skip conditions, and type conversions.
    """

    def setUp(self):
        """Initialize test GUIDs for serialization validation."""
        self.test_guid = Guid(UUID("12345678-1234-5678-9ABC-123456789ABC"))
        self.test_guid2 = Guid(UUID("87654321-4321-8765-CBA9-987654321CBA"))

    def test_write_guid(self):
        """Validate GUID serialization with skip conditions."""
        result = write_guid("TestProp", self.test_guid)
        self.assertEqual(result, "TestProp:'{12345678-1234-5678-9ABC-123456789ABC}'")
        result = write_guid("TestProp", NIL_GUID)
        self.assertEqual(result, "")
        result = write_guid("TestProp", self.test_guid, skip=self.test_guid)
        self.assertEqual(result, "")
        result = write_guid("TestProp", self.test_guid, skip=self.test_guid2)
        self.assertEqual(result, "TestProp:'{12345678-1234-5678-9ABC-123456789ABC}'")

    def test_write_guid_no_skip(self):
        """Validate mandatory GUID serialization without skip logic."""
        result = write_guid_no_skip("TestProp", self.test_guid)
        self.assertEqual(result, "TestProp:'{12345678-1234-5678-9ABC-123456789ABC}'")
        result = write_guid_no_skip("TestProp", NIL_GUID)
        self.assertEqual(result, "TestProp:'{00000000-0000-0000-0000-000000000000}'")

    def test_write_quote_string(self):
        """Validate quoted string serialization with empty string handling."""
        result = write_quote_string("TestProp", "test_value")
        self.assertEqual(result, "TestProp:'test_value'")
        result = write_quote_string("TestProp", "")
        self.assertEqual(result, "")
        result = write_quote_string("TestProp", "skip_me", skip="skip_me")
        self.assertEqual(result, "")
        result = write_quote_string("TestProp", "keep_me", skip="skip_me")
        self.assertEqual(result, "TestProp:'keep_me'")
        result = write_quote_string("TestProp", "test with spaces")
        self.assertEqual(result, "TestProp:'test with spaces'")

    def test_write_quote_string_no_skip(self):
        """Validate mandatory quoted string serialization."""
        result = write_quote_string_no_skip("TestProp", "test_value")
        self.assertEqual(result, "TestProp:'test_value'")
        result = write_quote_string_no_skip("TestProp", "")
        self.assertEqual(result, "TestProp:''")

    def test_sanitize_quoted_string_no_quotes(self):
        """Validate that strings without quotes pass through unchanged."""
        result = sanitize_quoted_string("normal_string")
        self.assertEqual(result, "normal_string")
        result = sanitize_quoted_string("string with spaces")
        self.assertEqual(result, "string with spaces")
        result = sanitize_quoted_string("")
        self.assertEqual(result, "")

    def test_sanitize_quoted_string_with_quotes(self):
        """Validate that single quotes are replaced with underscores."""
        result = sanitize_quoted_string("Bob's Node")
        self.assertEqual(result, "Bob_s Node")
        result = sanitize_quoted_string("It's a 'test'")
        self.assertEqual(result, "It_s a _test_")
        result = sanitize_quoted_string("'")
        self.assertEqual(result, "_")
        result = sanitize_quoted_string("'''")
        self.assertEqual(result, "___")

    def test_write_quote_string_sanitizes_quotes(self):
        """Validate that write_quote_string sanitizes single quotes."""
        result = write_quote_string("Name", "Bob's Node")
        self.assertEqual(result, "Name:'Bob_s Node'")
        result = write_quote_string("Name", "It's a 'test'")
        self.assertEqual(result, "Name:'It_s a _test_'")

    def test_write_quote_string_no_skip_sanitizes_quotes(self):
        """Validate that write_quote_string_no_skip sanitizes single quotes."""
        result = write_quote_string_no_skip("Name", "Bob's Node")
        self.assertEqual(result, "Name:'Bob_s Node'")
        result = write_quote_string_no_skip("Name", "It's a 'test'")
        self.assertEqual(result, "Name:'It_s a _test_'")

    def test_sanitize_quoted_string_logs_warning(self):
        """Validate that sanitization logs a warning with context."""
        with patch("pyptp.elements.serialization_helpers.logger.warning") as mock_log:
            result = sanitize_quoted_string("Bob's Node", "Name")
            self.assertEqual(result, "Bob_s Node")
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            self.assertIn("Name", str(call_args))
            self.assertIn("Bob's Node", str(call_args))
            self.assertIn("Bob_s Node", str(call_args))

    def test_sanitize_quoted_string_no_warning_for_clean_strings(self):
        """Validate that clean strings do not trigger warnings."""
        with patch("pyptp.elements.serialization_helpers.logger.warning") as mock_log:
            result = sanitize_quoted_string("Clean String", "Name")
            self.assertEqual(result, "Clean String")
            mock_log.assert_not_called()

    def test_write_string_no_skip(self):
        """Validate unquoted string serialization."""
        result = write_string_no_skip("TestProp", "test_value")
        self.assertEqual(result, "TestProp:test_value")
        result = write_string_no_skip("TestProp", "")
        self.assertEqual(result, "TestProp:")

    def test_write_float_no_skip(self):
        """Validate floating-point number serialization."""
        result = write_float_no_skip("TestProp", 3.14)
        self.assertEqual(result, "TestProp:3.14")
        result = write_float_no_skip("TestProp", 0.0)
        self.assertEqual(result, "TestProp:0.0")
        result = write_float_no_skip("TestProp", -1.5)
        self.assertEqual(result, "TestProp:-1.5")

    def test_write_double(self):
        """Validate double precision serialization with zero-skip logic."""
        result = write_double("TestProp", 3.14)
        self.assertEqual(result, "TestProp:3.14")
        result = write_double("TestProp", 0.0)
        self.assertEqual(result, "")
        result = write_double("TestProp", 3.14, skip=3.14)
        self.assertEqual(result, "")
        result = write_double("TestProp", 3.14, skip=2.71)
        self.assertEqual(result, "TestProp:3.14")
        result = write_double("TestProp", -1.5)
        self.assertEqual(result, "TestProp:-1.5")

    def test_write_double_no_skip(self):
        """Validate mandatory double precision serialization."""
        result = write_double_no_skip("TestProp", 3.14)
        self.assertEqual(result, "TestProp:3.14")
        result = write_double_no_skip("TestProp", 0.0)
        self.assertEqual(result, "TestProp:0.0")

    def test_write_boolean(self):
        """Validate boolean serialization with false-skip logic."""
        result = write_boolean("TestProp", value=True)
        self.assertEqual(result, "TestProp:True")
        result = write_boolean("TestProp", value=False)
        self.assertEqual(result, "")
        result = write_boolean("TestProp", value=True, skip=True)
        self.assertEqual(result, "")
        result = write_boolean("TestProp", value=False, skip=True)
        self.assertEqual(result, "TestProp:False")

    def test_write_boolean_no_skip(self):
        """Validate mandatory boolean serialization."""
        result = write_boolean_no_skip("TestProp", value=True)
        self.assertEqual(result, "TestProp:True")
        result = write_boolean_no_skip("TestProp", value=False)
        self.assertEqual(result, "TestProp:False")

    def test_write_integer(self):
        """Validate integer serialization with zero-skip logic."""
        result = write_integer("TestProp", 42)
        self.assertEqual(result, "TestProp:42")
        result = write_integer("TestProp", 0)
        self.assertEqual(result, "")
        result = write_integer("TestProp", 42, skip=42)
        self.assertEqual(result, "")
        result = write_integer("TestProp", 42, skip=24)
        self.assertEqual(result, "TestProp:42")
        result = write_integer("TestProp", -5)
        self.assertEqual(result, "TestProp:-5")
        result = write_integer("TestProp", int(3.14))
        self.assertEqual(result, "TestProp:3")

    def test_write_integer_no_skip(self):
        """Validate mandatory integer serialization."""
        result = write_integer_no_skip("TestProp", 42)
        self.assertEqual(result, "TestProp:42")
        result = write_integer_no_skip("TestProp", 0)
        self.assertEqual(result, "TestProp:0")
        result = write_integer_no_skip("TestProp", int(3.14))
        self.assertEqual(result, "TestProp:3")

    def test_write_color(self):
        """Validate color value serialization with zero-skip logic."""
        result = write_color("TestProp", 0xFF0000)
        self.assertEqual(result, "TestProp:0x00ff0000")
        result = write_color("TestProp", 0)
        self.assertEqual(result, "")
        result = write_color("TestProp", 0xFF0000, skip=0xFF0000)
        self.assertEqual(result, "")
        result = write_color("TestProp", 0xFF0000, skip=0x00FF00)
        self.assertEqual(result, "TestProp:0x00ff0000")
        result = write_color("TestProp", 0xFFFFFF)
        self.assertEqual(result, "TestProp:0x00ffffff")

    def test_write_color_no_skip(self):
        """Validate mandatory color value serialization."""
        result = write_color_no_skip("TestProp", 0xFF0000)
        self.assertEqual(result, "TestProp:0x00ff0000")
        result = write_color_no_skip("TestProp", 0)
        self.assertEqual(result, "TestProp:0x00000000")

    def test_write_delphi_color(self):
        """Validate Delphi-format color serialization."""
        result = write_delphi_color("TestProp", CL_RED)
        self.assertEqual(result, "TestProp:$0000FF")


if __name__ == "__main__":
    unittest.main()
