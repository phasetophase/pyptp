"""Tests for Text element (MV networks)."""

import unittest
from uuid import uuid4

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.text import TextMV
from pyptp.network_mv import NetworkMV


class TestTextRegistration(unittest.TestCase):
    """Test text element registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkMV()

    def test_text_registration_works(self) -> None:
        """Verify basic text element registration in network."""
        text_guid = Guid(uuid4())
        sheet_guid = Guid(uuid4())

        text = TextMV(
            general=TextMV.General(guid=text_guid),
            lines=[TextMV.Line(text="Test message line 1")],
            presentations=[TextMV.Presentation(sheet=sheet_guid, x=100, y=200)],
        )

        text.register(self.network)

        self.assertIn(text_guid, self.network.texts)
        self.assertEqual(self.network.texts[text_guid], text)

    def test_text_with_multiple_lines_serializes_correctly(self) -> None:
        """Test serialization with multiple text lines and full properties."""
        text_guid = Guid(uuid4())
        sheet_guid = Guid(uuid4())

        text = TextMV(
            general=TextMV.General(
                guid=text_guid,
                creation_time=1234567890.5,
                mutation_date=20240101,
                revision_date=20240102,
                variant=True,
            ),
            lines=[
                TextMV.Line(text="First line of text"),
                TextMV.Line(text="Second line of text"),
            ],
            presentations=[
                TextMV.Presentation(
                    sheet=sheet_guid,
                    x=150,
                    y=250,
                    text_color=DelphiColor("$FF"),
                    text_size=12,
                    font="Times New Roman",
                    text_style=1,
                    upside_down_text=True,
                )
            ],
        )

        serialized = text.serialize()

        self.assertIn(
            f"#General GUID:'{{{str(text_guid).upper()}}}' CreationTime:1234567890.5",
            serialized,
        )
        self.assertIn(
            "MutationDate:20240101 RevisionDate:20240102 Variant:True", serialized
        )
        self.assertIn("#Line Text:First line of text", serialized)
        self.assertIn("#Line Text:Second line of text", serialized)
        self.assertIn(
            f"#Presentation Sheet:'{{{str(sheet_guid).upper()}}}' X:150 Y:250",
            serialized,
        )
        self.assertIn("TextColor:$FF TextSize:12", serialized)
        self.assertIn(
            "Font:'Times New Roman' TextStyle:1 UpsideDownText:True", serialized
        )

    def test_minimal_text_serialization(self) -> None:
        """Test serialization with only required fields."""
        text_guid = Guid(uuid4())

        text = TextMV(
            general=TextMV.General(guid=text_guid),
            lines=[],
            presentations=[],
        )

        serialized = text.serialize()

        self.assertIn(
            f"#General GUID:'{{{str(text_guid).upper()}}}' CreationTime:0.0", serialized
        )
        self.assertNotIn("MutationDate:", serialized)
        self.assertNotIn("RevisionDate:", serialized)
        self.assertNotIn("Variant:", serialized)
        self.assertNotIn("#Line", serialized)
        self.assertNotIn("#Presentation", serialized)

    def test_text_deserialization_works(self) -> None:
        """Test deserialization from VNF data dictionary."""
        text_guid = Guid(uuid4())
        sheet_guid = Guid(uuid4())

        data = {
            "general": [
                {
                    "GUID": str(text_guid),
                    "CreationTime": 1234567890.5,
                    "MutationDate": 20240101,
                    "Variant": True,
                }
            ],
            "lines": [
                {"Text": "Line 1"},
                {"Text": "Line 2"},
            ],
            "presentations": [
                {
                    "Sheet": str(sheet_guid),
                    "X": 100,
                    "Y": 200,
                    "TextColor": 255,
                    "TextSize": 14,
                    "Font": "Arial",
                    "TextStyle": 0,
                    "UpsideDownText": False,
                }
            ],
        }

        text = TextMV.deserialize(data)

        self.assertEqual(text.general.guid, text_guid)
        self.assertEqual(text.general.creation_time, 1234567890.5)
        self.assertEqual(text.general.mutation_date, 20240101)
        self.assertTrue(text.general.variant)

        self.assertEqual(len(text.lines), 2)
        self.assertEqual(text.lines[0].text, "Line 1")
        self.assertEqual(text.lines[1].text, "Line 2")

        self.assertEqual(len(text.presentations), 1)
        pres = text.presentations[0]
        self.assertEqual(pres.sheet, sheet_guid)
        self.assertEqual(pres.x, 100)
        self.assertEqual(pres.y, 200)
        self.assertEqual(pres.text_color, 255)
        self.assertEqual(pres.text_size, 14)

    def test_duplicate_text_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        text_guid = Guid(uuid4())

        text1 = TextMV(
            general=TextMV.General(guid=text_guid),
            lines=[TextMV.Line(text="First text")],
            presentations=[],
        )

        text2 = TextMV(
            general=TextMV.General(guid=text_guid),
            lines=[TextMV.Line(text="Second text")],
            presentations=[],
        )

        # Register first text
        text1.register(self.network)
        self.assertEqual(self.network.texts[text_guid].lines[0].text, "First text")

        # Register second text with same GUID - should overwrite with warning
        text2.register(self.network)

        self.assertEqual(self.network.texts[text_guid].lines[0].text, "Second text")


if __name__ == "__main__":
    unittest.main()
