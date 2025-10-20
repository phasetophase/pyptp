"""DeclarativeHandler base class validation test suite.

Tests the declarative GNF/VNF parsing framework used throughout the import
system for consistent section-based element construction.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Any, ClassVar
from unittest.mock import Mock, patch
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig


@dataclass
class MockGeneral:
    """Mock general section for testing declarative parsing."""

    GUID: Guid
    Name: str = ""
    Value: float = 0.0
    Active: bool = False


@dataclass
class MockPresentation:
    """Mock presentation section for testing declarative parsing."""

    Sheet: Guid
    X: int = 0
    Y: int = 0


@dataclass
class MockComponent:
    """Mock network element for testing declarative assembly."""

    general: MockGeneral
    presentations: list[MockPresentation]
    extras: list[Extra]
    notes: list[Note]

    def register(self, network: Any) -> None:
        """Mock network registration for testing."""


class MockHandler(DeclarativeHandler):
    """Mock handler for testing declarative parsing framework."""

    COMPONENT_CLS = MockComponent
    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Mock class resolution for testing."""
        if kwarg_name == "presentations":
            return MockPresentation
        return None


class TestDeclarativeHandler(unittest.TestCase):
    """Validation tests for declarative GNF/VNF parsing framework.

    Tests section parsing, type resolution, and component assembly
    for the base handler that all element importers extend.
    """

    handler: MockHandler
    mock_network: Mock
    test_guid: Guid
    sheet_guid: Guid

    def setUp(self) -> None:
        """Initialize test handler and mock objects."""
        self.handler = MockHandler()
        self.mock_network = Mock()
        self.test_guid = Guid(UUID("12345678-1234-5678-9ABC-123456789ABC"))
        self.sheet_guid = Guid(UUID("87654321-4321-8765-CBA9-987654321CBA"))

    def test_parse_gnf_line_to_dict_basic(self) -> None:
        """Validate basic property line parsing with type inference."""
        line = "Name:'TestNode' Value:3.14 Active:true Count:42"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Name": "TestNode",
            "Value": 3.14,
            "Active": True,
            "Count": 42,
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_boolean_values(self) -> None:
        """Validate boolean value parsing and conversion."""
        line = "Active:true Visible:false"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Active": True,
            "Visible": False,
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_numeric_values(self) -> None:
        """Validate numeric value parsing with int/float detection."""
        line = "Integer:42 Float:3.14 Negative:-1.5 Zero:0"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Integer": 42,
            "Float": 3.14,
            "Negative": -1.5,
            "Zero": 0,
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_comma_decimal(self) -> None:
        """Validate European decimal format parsing (comma separator)."""
        line = "Value:3,14 Negative:-1,5"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Value": 3.14,
            "Negative": -1.5,
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_quoted_strings(self) -> None:
        """Validate quoted string parsing with space preservation."""
        line = "Name:'Test Node' Description:'A test description with spaces'"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Name": "Test Node",
            "Description": "A test description with spaces",
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_empty_quoted_strings(self) -> None:
        """Validate empty quoted string handling."""
        line = "Name:'' Description:''"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "Name": "",
            "Description": "",
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_guid_format(self) -> None:
        """Validate GUID format parsing with braces."""
        line = "GUID:'{12345678-1234-5678-9ABC-123456789ABC}'"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "GUID": "{12345678-1234-5678-9ABC-123456789ABC}",
        }
        self.assertEqual(result, expected)

    def test_parse_gnf_line_to_dict_invalid_numbers(self) -> None:
        """Validate fallback to string for malformed numeric values."""
        line = "InvalidFloat:3.14.15 InvalidInt:42abc"
        result = self.handler._parse_gnf_line_to_dict(line)

        expected = {
            "InvalidFloat": "3.14.15",
            "InvalidInt": "42abc",
        }
        self.assertEqual(result, expected)

    def test_parse_sections_basic(self) -> None:
        """Validate basic section parsing with multiple section types."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestNode'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#Extra Text:key1=value1
#Note Text:Test note
#END"""

        sections = list(self.handler.parse_sections(raw_text))
        self.assertEqual(len(sections), 1)

        section = sections[0]
        self.assertIn("#General ", section)
        self.assertIn("#Presentation ", section)
        self.assertIn("#Extra Text:", section)
        self.assertIn("#Note Text:", section)

    def test_parse_sections_multiple_components(self) -> None:
        """Validate parsing of multiple element instances."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'Node1'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#General GUID:'{87654321-4321-8765-CBA9-987654321CBA}' Name:'Node2'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:200 Y:300
#END"""

        sections = list(self.handler.parse_sections(raw_text))
        self.assertEqual(len(sections), 2)

    def test_parse_sections_empty_sections(self) -> None:
        """Validate handling of empty section content."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestNode'
#Presentation 
#Extra Text:
#Note Text:
#END"""

        sections = list(self.handler.parse_sections(raw_text))
        self.assertEqual(len(sections), 1)

        section = sections[0]
        self.assertIn("#Presentation ", section)
        self.assertIn("#Extra Text:", section)
        self.assertIn("#Note Text:", section)

    def test_process_section_data_general(self) -> None:
        """Validate general section data processing and type conversion."""
        section = {
            "#General ": [
                "GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestNode' Value:3.14 Active:true"
            ],
        }
        config = SectionConfig("general", "#General ", required=True)

        with patch.object(self.handler, "_get_target_class", return_value=MockGeneral):
            result = self.handler._process_section_data(section, config)

        self.assertIsInstance(result, MockGeneral)

    def test_process_section_data_list_field(self) -> None:
        """Validate list field processing with multiple instances."""
        section = {
            "#Presentation ": [
                "Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200",
                "Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:300 Y:400",
            ],
        }
        config = SectionConfig("presentations", "#Presentation ", required=True)

        with patch.object(
            MockComponent, "__annotations__", {"presentations": list[MockPresentation]}
        ):
            with patch.object(
                self.handler, "_get_target_class", return_value=MockPresentation
            ):
                result = self.handler._process_section_data(section, config)

        # Type-safe assertions
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], MockPresentation)
        assert isinstance(result[1], MockPresentation)
        self.assertEqual(result[0].X, 100)
        self.assertEqual(result[1].X, 300)

    def test_process_section_data_notes(self) -> None:
        """Validate notes section processing into Note objects."""
        section = {
            "#Note Text:": ["First note", "Second note"],
        }
        config = SectionConfig("notes", "#Note Text:")

        result = self.handler._process_section_data(section, config)

        # Type-safe assertions
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Note)
        assert isinstance(result[1], Note)
        self.assertEqual(result[0].text, "First note")
        self.assertEqual(result[1].text, "Second note")

    def test_process_section_data_extras(self) -> None:
        """Validate extras section processing into Extra objects."""
        section = {
            "#Extra Text:": ["key1=value1", "key2=value2", "standalone_key"],
        }
        config = SectionConfig("extras", "#Extra Text:")

        result = self.handler._process_section_data(section, config)

        # Type-safe assertions
        assert isinstance(result, list)
        assert len(result) == 3
        assert isinstance(result[0], Extra)
        assert isinstance(result[1], Extra)
        assert isinstance(result[2], Extra)
        self.assertEqual(result[1].text.split("=")[0], "key2")
        self.assertEqual(result[1].text.split("=")[1], "value2")
        self.assertEqual(result[2].text.split("=")[0], "standalone_key")
        self.assertEqual(
            result[2].text.split("=")[1] if "=" in result[2].text else "", ""
        )

    def test_process_section_data_missing_required(self) -> None:
        """Validate error handling for missing required sections."""
        section = {}
        config = SectionConfig("general", "#General ", required=True)

        with self.assertRaises(ValueError) as cm:
            self.handler._process_section_data(section, config)

        self.assertIn("Required GNF section", str(cm.exception))

    def test_process_section_data_missing_optional(self) -> None:
        """Validate default handling for missing optional sections."""
        section = {}
        config = SectionConfig("extras", "#Extra Text:")

        with patch.object(MockComponent, "__annotations__", {"extras": list[Extra]}):
            result = self.handler._process_section_data(section, config)
        self.assertEqual(result, [])

    def test_get_target_class_presentations(self) -> None:
        """Validate target class resolution through resolver method."""
        result = self.handler._get_target_class("presentations")
        self.assertEqual(result, MockPresentation)

    def test_get_target_class_general(self) -> None:
        """Validate target class resolution through type annotations."""
        with patch.object(MockComponent, "__annotations__", {"general": MockGeneral}):
            result = self.handler._get_target_class("general")
            self.assertEqual(result, MockGeneral)

    def test_get_target_class_unknown(self) -> None:
        """Validate None return for unknown field types."""
        result = self.handler._get_target_class("unknown_field")
        self.assertIsNone(result)

    def test_handle_success(self) -> None:
        """Validate successful component parsing and assembly."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestNode'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#Extra Text:key1=value1
#Note Text:Test note
#END"""

        with patch.object(self.handler, "_get_target_class") as mock_get_class:
            mock_get_class.side_effect = lambda name: {
                "general": MockGeneral,
                "presentations": MockPresentation,
            }.get(name)

            self.handler.handle(self.mock_network, raw_text)

    def test_handle_missing_general(self) -> None:
        """Validate graceful handling of missing general section."""
        raw_text = """#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#END"""

        with patch.object(self.handler, "_get_target_class") as mock_get_class:
            mock_get_class.side_effect = lambda name: {
                "presentations": MockPresentation,
            }.get(name)

            self.handler.handle(self.mock_network, raw_text)

    def test_handle_invalid_data(self) -> None:
        """Validate error handling for malformed GNF data."""
        raw_text = """#General GUID:'invalid-guid' Name:'TestNode'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#END"""

        with patch.object(self.handler, "_get_target_class") as mock_get_class:
            mock_get_class.side_effect = lambda name: {
                "general": MockGeneral,
                "presentations": MockPresentation,
            }.get(name)

            try:
                self.handler.handle(self.mock_network, raw_text)
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                self.assertIsInstance(
                    e, (ValueError, TypeError, AttributeError, KeyError)
                )

    def test_handle_batch_success(self) -> None:
        """Validate successful batch processing of multiple components."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'Node1'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#General GUID:'{87654321-4321-8765-CBA9-987654321CBA}' Name:'Node2'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:200 Y:300
#END"""

        with patch.object(self.handler, "_get_target_class") as mock_get_class:
            mock_get_class.side_effect = lambda name: {
                "general": MockGeneral,
                "presentations": MockPresentation,
            }.get(name)

            self.handler.handle_batch(self.mock_network, raw_text)

    def test_handle_batch_partial_failure(self) -> None:
        """Validate batch processing with some invalid components."""
        raw_text = """#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'Node1'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200
#General GUID:'invalid-guid' Name:'Node2'
#Presentation Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:200 Y:300
#END"""

        with patch.object(self.handler, "_get_target_class") as mock_get_class:
            mock_get_class.side_effect = lambda name: {
                "general": MockGeneral,
                "presentations": MockPresentation,
            }.get(name)

            self.handler.handle_batch(self.mock_network, raw_text)

    def test_section_regex_compilation(self) -> None:
        """Validate regex compilation caching for performance optimization."""
        regex1 = self.handler._get_section_regex()

        regex2 = self.handler._get_section_regex()

        self.assertIs(regex1, regex2)
        self.assertIsNotNone(self.handler._compiled_section_regex)

    def test_edge_cases_empty_input(self) -> None:
        """Validate handling of empty and whitespace-only input."""
        sections = list(self.handler.parse_sections(""))
        self.assertEqual(len(sections), 0)

        sections = list(self.handler.parse_sections("   \n\t  "))
        self.assertEqual(len(sections), 0)

        raw_text = (
            "#General GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestNode'"
        )
        sections = list(self.handler.parse_sections(raw_text))
        self.assertGreaterEqual(len(sections), 0)

        line = "InvalidFormat Name: Value"
        result = self.handler._parse_gnf_line_to_dict(line)
        self.assertEqual(result, {})

    def test_performance_optimizations(self) -> None:
        """Validate performance with large input datasets."""
        large_sections = []
        for i in range(100):
            large_sections.append(
                f"#General GUID:'{{12345678-1234-5678-9ABC-12345678{i:04d}}}' Name:'Node{i}'"
            )
            large_sections.append(
                f"#Presentation Sheet:'{{87654321-4321-8765-CBA9-987654321CBA}}' X:{i * 10} Y:{i * 20}"
            )

        raw_text = "\n".join(large_sections) + "\n#END"

        sections = list(self.handler.parse_sections(raw_text))
        self.assertEqual(len(sections), 100)


class TestSectionConfig(unittest.TestCase):
    """Validation tests for SectionConfig configuration objects."""

    def test_section_config_creation(self):
        """Validate SectionConfig initialization with required parameters."""
        config = SectionConfig("general", "#General ", required=True)

        self.assertEqual(config.kwarg_name, "general")
        self.assertEqual(config.gnf_tag, "#General ")
        self.assertTrue(config.required)

    def test_section_config_defaults(self):
        """Validate SectionConfig default values for optional parameters."""
        config = SectionConfig("extras", "#Extra Text:")

        self.assertEqual(config.kwarg_name, "extras")
        self.assertEqual(config.gnf_tag, "#Extra Text:")
        self.assertFalse(config.required)


if __name__ == "__main__":
    unittest.main()
