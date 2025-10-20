"""Test demonstration of empty section handling in serialization."""

from __future__ import annotations

import unittest

from pyptp.elements.lv.shared import Fields
from pyptp.elements.serialization_helpers import write_section_if_not_empty


class TestEmptySectionHandling(unittest.TestCase):
    """Demonstrate empty section handling in serialization."""

    def test_empty_section_handling_demonstration(self):
        """Demonstrate how empty sections are handled."""
        fields = Fields(values=[])
        old_way = f"#Fields {fields.serialize()}"
        new_way = write_section_if_not_empty("Fields", fields.serialize())
        self.assertEqual(old_way, "#Fields ")
        self.assertEqual(new_way, "")

    def test_non_empty_section_handling(self):
        """Demonstrate that non-empty sections are still written."""
        fields = Fields(values=["Test1", "Test2"])
        old_way = f"#Fields {fields.serialize()}"
        new_way = write_section_if_not_empty("Fields", fields.serialize())
        self.assertEqual(old_way, new_way)
        self.assertIn("Name0:'Test1'", new_way)
        self.assertIn("Name1:'Test2'", new_way)

    def test_improved_element_serialization_pattern(self):
        """Show how to improve element serialization patterns."""
        general_content = (
            "GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'TestElement'"
        )
        fields_content = ""
        presentation_content = (
            "Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200"
        )
        extras_content = ""
        notes_content = ""
        old_lines = [
            f"#General {general_content}",
            f"#Fields {fields_content}",
            f"#Presentation {presentation_content}",
            f"#Extra Text:{extras_content}",
            f"#Note Text:{notes_content}",
        ]
        old_serialized = "\n".join(old_lines)
        new_lines = []
        new_lines.append(f"#General {general_content}")
        fields_line = write_section_if_not_empty("Fields", fields_content)
        if fields_line:
            new_lines.append(fields_line)
        new_lines.append(f"#Presentation {presentation_content}")
        extras_line = write_section_if_not_empty("Extra Text", extras_content)
        if extras_line:
            new_lines.append(extras_line)
        notes_line = write_section_if_not_empty("Note Text", notes_content)
        if notes_line:
            new_lines.append(notes_line)
        new_serialized = "\n".join(new_lines)
        self.assertIn("#Fields ", old_serialized)
        self.assertNotIn("#Fields", new_serialized)
        self.assertIn("#Extra Text:", old_serialized)
        self.assertNotIn("#Extra Text:", new_serialized)
        self.assertIn("#Note Text:", old_serialized)
        self.assertNotIn("#Note Text:", new_serialized)
        self.assertIn("#General", new_serialized)
        self.assertIn("#Presentation", new_serialized)

    def test_comprehensive_serialization_helper(self):
        """Test a more comprehensive helper for element serialization."""

        def serialize_element_improved(
            general_content: str,
            optional_sections: dict[str, str | None],
            list_sections: dict[str, list[str]],
        ) -> str:
            """Improved element serialization that skips empty sections."""
            lines = [f"#General {general_content}"]
            for section_name, content in optional_sections.items():
                section_line = write_section_if_not_empty(section_name, content)
                if section_line:
                    lines.append(section_line)
            for section_name, items in list_sections.items():
                lines.extend(
                    f"#{section_name} {item}" for item in items if item.strip()
                )
            return "\n".join(lines)

        result = serialize_element_improved(
            general_content="GUID:'{12345678-1234-5678-9ABC-123456789ABC}' Name:'Test'",
            optional_sections={
                "Fields": "",
                "VoltageControl": "R:0.5 X:0.3",
                "TransformerType": None,
            },
            list_sections={
                "Presentation": [
                    "Sheet:'{87654321-4321-8765-CBA9-987654321CBA}' X:100 Y:200"
                ],
                "Extra Text": [],
                "Note Text": ["Important note"],
            },
        )
        self.assertIn("#General", result)
        self.assertIn("#VoltageControl", result)
        self.assertIn("#Presentation", result)
        self.assertIn("#Note Text", result)
        self.assertNotIn("#Fields", result)
        self.assertNotIn("#TransformerType", result)
        self.assertNotIn("#Extra Text", result)


if __name__ == "__main__":
    unittest.main()
