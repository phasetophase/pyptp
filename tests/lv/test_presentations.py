"""Tests for presentation classes."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.color_utils import CL_BLACK, CL_BLUE, CL_RED
from pyptp.elements.element_utils import NIL_GUID, Guid, encode_guid
from pyptp.elements.lv.presentations import (
    BranchPresentation,
    ElementPresentation,
    NodePresentation,
    SecundairPresentation,
)


class TestNodePresentation(unittest.TestCase):
    """Test NodePresentation serialization and deserialization behavior."""

    def setUp(self) -> None:
        """Create fresh dependencies for isolated testing."""
        self.test_guid = Guid(uuid4())

    def test_node_presentation_serialize_with_defaults(self) -> None:
        """Test NodePresentation serialization with default values."""
        node_presentation = NodePresentation()

        result = node_presentation.serialize()

        # Should include required fields
        self.assertIn(f"Sheet:{encode_guid(NIL_GUID)}", result)
        self.assertIn("X:0", result)
        self.assertIn("Y:0", result)
        self.assertIn("Symbol:11", result)
        self.assertIn(f"Color:{CL_BLACK}", result)

        # Should skip default values
        self.assertNotIn("Size:", result)  # Default 1 should be skipped
        self.assertNotIn("Width:", result)  # Default 1 should be skipped
        self.assertNotIn("TextSize:", result)  # Default 10 should be skipped
        self.assertNotIn("Font:", result)  # Default "Arial" should be skipped
        self.assertNotIn("TextStyle:", result)  # Default 0 should be skipped
        self.assertNotIn("NoText:", result)  # Default False should be skipped
        self.assertNotIn("UpsideDownText:", result)  # Default False should be skipped
        self.assertNotIn("TextRotation:", result)  # Default 0 should be skipped

    def test_node_presentation_serialize_with_full_properties(self) -> None:
        """Test NodePresentation serialization with all properties set."""
        node_presentation = NodePresentation(
            sheet=self.test_guid,
            x=100,
            y=200,
            symbol=15,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            text_rotation=90,
            upstrings_x=10,
            upstrings_y=20,
            fault_strings_x=30,
            fault_strings_y=40,
            note_x=50,
            note_y=60,
        )

        result = node_presentation.serialize()

        # Verify all properties are included
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn("X:100", result)
        self.assertIn("Y:200", result)
        self.assertIn("Symbol:15", result)
        self.assertIn(f"Color:{CL_RED}", result)
        self.assertIn("Size:2", result)
        self.assertIn("Width:3", result)
        self.assertIn(f"TextColor:{CL_BLUE}", result)
        self.assertIn("TextSize:12", result)
        self.assertIn("Font:'Times'", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)
        self.assertIn("TextRotation:90", result)
        self.assertIn("UpstringsX:10", result)
        self.assertIn("UpstringsY:20", result)
        self.assertIn("FaultStringsX:30", result)
        self.assertIn("FaultStringsY:40", result)
        self.assertIn("NoteX:50", result)
        self.assertIn("NoteY:60", result)

    def test_node_presentation_deserialization_works(self) -> None:
        """Test NodePresentation deserialization from dictionary data."""
        data = {
            "Sheet": str(self.test_guid),
            "X": 100,
            "Y": 200,
            "Symbol": 15,
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 12,
            "Font": "Times",
            "TextStyle": 1,
            "NoText": True,
            "UpsideDownText": True,
            "TextRotation": 90,
            "UpstringsX": 10,
            "UpstringsY": 20,
            "FaultStringsX": 30,
            "FaultStringsY": 40,
            "NoteX": 50,
            "NoteY": 60,
        }

        node_presentation = NodePresentation.deserialize(data)

        # Verify all properties
        self.assertEqual(node_presentation.sheet, self.test_guid)
        self.assertEqual(node_presentation.x, 100)
        self.assertEqual(node_presentation.y, 200)
        self.assertEqual(node_presentation.symbol, 15)
        self.assertEqual(node_presentation.color, CL_RED)
        self.assertEqual(node_presentation.size, 2)
        self.assertEqual(node_presentation.width, 3)
        self.assertEqual(node_presentation.text_color, CL_BLUE)
        self.assertEqual(node_presentation.text_size, 12)
        self.assertEqual(node_presentation.font, "Times")
        self.assertEqual(node_presentation.text_style, 1)
        self.assertEqual(node_presentation.no_text, True)
        self.assertEqual(node_presentation.upside_down_text, True)
        self.assertEqual(node_presentation.text_rotation, 90)
        self.assertEqual(node_presentation.upstrings_x, 10)
        self.assertEqual(node_presentation.upstrings_y, 20)
        self.assertEqual(node_presentation.fault_strings_x, 30)
        self.assertEqual(node_presentation.fault_strings_y, 40)
        self.assertEqual(node_presentation.note_x, 50)
        self.assertEqual(node_presentation.note_y, 60)

    def test_node_presentation_deserialization_with_empty_data(self) -> None:
        """Test NodePresentation deserialization with empty data."""
        data = {}

        node_presentation = NodePresentation.deserialize(data)

        # Should have default values
        self.assertEqual(node_presentation.sheet, NIL_GUID)
        self.assertEqual(node_presentation.x, 0)
        self.assertEqual(node_presentation.y, 0)
        self.assertEqual(node_presentation.symbol, 11)
        self.assertEqual(node_presentation.color, CL_BLACK)
        self.assertEqual(node_presentation.size, 1)
        self.assertEqual(node_presentation.width, 1)
        self.assertEqual(node_presentation.text_color, CL_BLACK)
        self.assertEqual(node_presentation.text_size, 10)
        self.assertEqual(node_presentation.font, "Arial")
        self.assertEqual(node_presentation.text_style, 0)
        self.assertEqual(node_presentation.no_text, False)
        self.assertEqual(node_presentation.upside_down_text, False)
        self.assertEqual(node_presentation.text_rotation, 0)

    def test_node_presentation_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original = NodePresentation(
            sheet=self.test_guid,
            x=100,
            y=200,
            symbol=15,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            text_rotation=90,
        )

        original.serialize()

        # Simulate parsing back from serialized format
        data = {
            "Sheet": str(self.test_guid),
            "X": 100,
            "Y": 200,
            "Symbol": 15,
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 12,
            "Font": "Times",
            "TextStyle": 1,
            "NoText": True,
            "UpsideDownText": True,
            "TextRotation": 90,
        }

        deserialized = NodePresentation.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.sheet, original.sheet)
        self.assertEqual(deserialized.x, original.x)
        self.assertEqual(deserialized.y, original.y)
        self.assertEqual(deserialized.symbol, original.symbol)
        self.assertEqual(deserialized.color, original.color)
        self.assertEqual(deserialized.size, original.size)
        self.assertEqual(deserialized.width, original.width)
        self.assertEqual(deserialized.text_color, original.text_color)
        self.assertEqual(deserialized.text_size, original.text_size)
        self.assertEqual(deserialized.font, original.font)
        self.assertEqual(deserialized.text_style, original.text_style)
        self.assertEqual(deserialized.no_text, original.no_text)
        self.assertEqual(deserialized.upside_down_text, original.upside_down_text)
        self.assertEqual(deserialized.text_rotation, original.text_rotation)


class TestBranchPresentation(unittest.TestCase):
    """Test BranchPresentation serialization and deserialization behavior."""

    def setUp(self) -> None:
        """Create fresh dependencies for isolated testing."""
        self.test_guid = Guid(uuid4())

    def test_branch_presentation_serialize_with_defaults(self) -> None:
        """Test BranchPresentation serialization with default values."""
        branch_presentation = BranchPresentation()

        result = branch_presentation.serialize()

        # Should include required fields
        self.assertIn(f"Sheet:{encode_guid(NIL_GUID)}", result)
        self.assertIn(f"Color:{CL_BLACK}", result)

        # Should skip default values
        self.assertNotIn("Size:", result)  # Default 1 should be skipped
        self.assertNotIn("Width:", result)  # Default 1 should be skipped
        self.assertNotIn("TextSize:", result)  # Default 7 should be skipped
        self.assertNotIn("Font:", result)  # Default "Arial" should be skipped
        self.assertNotIn("TextStyle:", result)  # Default 0 should be skipped
        self.assertNotIn("NoText:", result)  # Default False should be skipped
        self.assertNotIn("UpsideDownText:", result)  # Default False should be skipped
        self.assertNotIn("FlagFlipped1:", result)  # Default False should be skipped
        self.assertNotIn("FlagFlipped2:", result)  # Default False should be skipped

        # Should not include empty coordinate lists
        self.assertNotIn("FirstCorners:", result)
        self.assertNotIn("SecondCorners:", result)

    def test_branch_presentation_serialize_with_coordinates(self) -> None:
        """Test BranchPresentation serialization with coordinates."""
        branch_presentation = BranchPresentation(
            sheet=self.test_guid,
            first_corners=[(10, 20), (30, 40)],
            second_corners=[(50, 60), (70, 80)],
            color=CL_RED,
            size=2,
            strings1_x=100,
            strings1_y=200,
        )

        result = branch_presentation.serialize()

        # Verify properties are included
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn(f"Color:{CL_RED}", result)
        self.assertIn("Size:2", result)
        self.assertIn("Strings1X:100", result)
        self.assertIn("Strings1Y:200", result)
        self.assertIn("FirstCorners:'{(10 20) (30 40) }'", result)
        self.assertIn("SecondCorners:'{(50 60) (70 80) }'", result)

    def test_branch_presentation_serialize_with_full_properties(self) -> None:
        """Test BranchPresentation serialization with all properties set."""
        branch_presentation = BranchPresentation(
            sheet=self.test_guid,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=8,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings1_x=10,
            strings1_y=20,
            strings2_x=30,
            strings2_y=40,
            mid_strings_x=50,
            mid_strings_y=60,
            fault_strings_x=70,
            fault_strings_y=80,
            note_x=90,
            note_y=100,
            flag_flipped1=True,
            flag_flipped2=True,
            first_corners=[(10, 20)],
            second_corners=[(30, 40)],
        )

        result = branch_presentation.serialize()

        # Verify all properties are included
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn(f"Color:{CL_RED}", result)
        self.assertIn("Size:2", result)
        self.assertIn("Width:3", result)
        self.assertIn(f"TextColor:{CL_BLUE}", result)
        self.assertIn("TextSize:8", result)
        self.assertIn("Font:'Times'", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)
        self.assertIn("Strings1X:10", result)
        self.assertIn("Strings1Y:20", result)
        self.assertIn("Strings2X:30", result)
        self.assertIn("Strings2Y:40", result)
        self.assertIn("MidStringsX:50", result)
        self.assertIn("MidStringsY:60", result)
        self.assertIn("FaultStringsX:70", result)
        self.assertIn("FaultStringsY:80", result)
        self.assertIn("NoteX:90", result)
        self.assertIn("NoteY:100", result)
        self.assertIn("FlagFlipped1:True", result)
        self.assertIn("FlagFlipped2:True", result)
        self.assertIn("FirstCorners:'{(10 20) }'", result)
        self.assertIn("SecondCorners:'{(30 40) }'", result)

    def test_branch_presentation_deserialization_works(self) -> None:
        """Test BranchPresentation deserialization from dictionary data."""
        data = {
            "Sheet": str(self.test_guid),
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 8,
            "Font": "Times",
            "FirstCorners": [(10, 20), (30, 40)],
            "SecondCorners": [(50, 60), (70, 80)],
            "Strings1X": 100,
            "Strings1Y": 200,
            "FlagFlipped1": True,
        }

        branch_presentation = BranchPresentation.deserialize(data)

        # Verify properties
        self.assertEqual(branch_presentation.sheet, self.test_guid)
        self.assertEqual(branch_presentation.color, CL_RED)
        self.assertEqual(branch_presentation.size, 2)
        self.assertEqual(branch_presentation.width, 3)
        self.assertEqual(branch_presentation.text_color, CL_BLUE)
        self.assertEqual(branch_presentation.text_size, 8)
        self.assertEqual(branch_presentation.font, "Times")
        self.assertEqual(branch_presentation.first_corners, [(10, 20), (30, 40)])
        self.assertEqual(branch_presentation.second_corners, [(50, 60), (70, 80)])
        self.assertEqual(branch_presentation.strings1_x, 100)
        self.assertEqual(branch_presentation.strings1_y, 200)
        self.assertEqual(branch_presentation.flag_flipped1, True)

    def test_branch_presentation_deserialization_with_empty_data(self) -> None:
        """Test BranchPresentation deserialization with empty data."""
        data = {}

        branch_presentation = BranchPresentation.deserialize(data)

        # Should have default values
        self.assertEqual(branch_presentation.sheet, NIL_GUID)
        self.assertEqual(branch_presentation.color, CL_BLACK)
        self.assertEqual(branch_presentation.size, 1)
        self.assertEqual(branch_presentation.width, 1)
        self.assertEqual(branch_presentation.text_color, CL_BLACK)
        self.assertEqual(branch_presentation.text_size, 7)
        self.assertEqual(branch_presentation.font, "Arial")
        self.assertEqual(branch_presentation.text_style, 0)
        self.assertEqual(branch_presentation.no_text, False)
        self.assertEqual(branch_presentation.upside_down_text, False)
        self.assertEqual(branch_presentation.flag_flipped1, False)
        self.assertEqual(branch_presentation.flag_flipped2, False)
        self.assertEqual(branch_presentation.first_corners, [])
        self.assertEqual(branch_presentation.second_corners, [])


class TestElementPresentation(unittest.TestCase):
    """Test ElementPresentation serialization and deserialization behavior."""

    def setUp(self) -> None:
        """Create fresh dependencies for isolated testing."""
        self.test_guid = Guid(uuid4())

    def test_element_presentation_serialize_with_defaults(self) -> None:
        """Test ElementPresentation serialization with default values."""
        element_presentation = ElementPresentation()

        result = element_presentation.serialize()

        # Should include required fields
        self.assertIn(f"Sheet:{encode_guid(NIL_GUID)}", result)
        self.assertIn("X:0", result)
        self.assertIn("Y:0", result)
        self.assertIn(f"Color:{CL_BLACK}", result)

        # Should skip default values
        self.assertNotIn("Size:", result)  # Default 1 should be skipped
        self.assertNotIn("Width:", result)  # Default 1 should be skipped
        self.assertNotIn("TextSize:", result)  # Default 7 should be skipped
        self.assertNotIn("Font:", result)  # Default "Arial" should be skipped
        self.assertNotIn("TextStyle:", result)  # Default 0 should be skipped
        self.assertNotIn("NoText:", result)  # Default False should be skipped
        self.assertNotIn("UpsideDownText:", result)  # Default False should be skipped
        self.assertNotIn("FlagFlipped:", result)  # Default False should be skipped

    def test_element_presentation_serialize_with_full_properties(self) -> None:
        """Test ElementPresentation serialization with all properties set."""
        element_presentation = ElementPresentation(
            sheet=self.test_guid,
            x=100,
            y=200,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings1_x=10,
            strings1_y=20,
            symbol_strings_x=30,
            symbol_strings_y=40,
            note_x=50,
            note_y=60,
            flag_flipped=True,
        )

        result = element_presentation.serialize()

        # Verify all properties are included
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn("X:100", result)
        self.assertIn("Y:200", result)
        self.assertIn(f"Color:{CL_RED}", result)
        self.assertIn("Size:2", result)
        self.assertIn("Width:3", result)
        self.assertIn(f"TextColor:{CL_BLUE}", result)
        self.assertIn("TextSize:12", result)
        self.assertIn("Font:'Times'", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)
        self.assertIn("Strings1X:10", result)
        self.assertIn("Strings1Y:20", result)
        self.assertIn("SymbolStringsX:30", result)
        self.assertIn("SymbolStringsY:40", result)
        self.assertIn("NoteX:50", result)
        self.assertIn("NoteY:60", result)
        self.assertIn("FlagFlipped:True", result)

    def test_element_presentation_deserialization_works(self) -> None:
        """Test ElementPresentation deserialization from dictionary data."""
        data = {
            "Sheet": str(self.test_guid),
            "X": 100,
            "Y": 200,
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 12,
            "Font": "Times",
            "TextStyle": 1,
            "NoText": True,
            "UpsideDownText": True,
            "Strings1X": 10,
            "Strings1Y": 20,
            "SymbolStringsX": 30,
            "SymbolStringsY": 40,
            "NoteX": 50,
            "NoteY": 60,
            "FlagFlipped": True,
        }

        element_presentation = ElementPresentation.deserialize(data)

        # Verify all properties
        self.assertEqual(element_presentation.sheet, self.test_guid)
        self.assertEqual(element_presentation.x, 100)
        self.assertEqual(element_presentation.y, 200)
        self.assertEqual(element_presentation.color, CL_RED)
        self.assertEqual(element_presentation.size, 2)
        self.assertEqual(element_presentation.width, 3)
        self.assertEqual(element_presentation.text_color, CL_BLUE)
        self.assertEqual(element_presentation.text_size, 12)
        self.assertEqual(element_presentation.font, "Times")
        self.assertEqual(element_presentation.text_style, 1)
        self.assertEqual(element_presentation.no_text, True)
        self.assertEqual(element_presentation.upside_down_text, True)
        self.assertEqual(element_presentation.strings1_x, 10)
        self.assertEqual(element_presentation.strings1_y, 20)
        self.assertEqual(element_presentation.symbol_strings_x, 30)
        self.assertEqual(element_presentation.symbol_strings_y, 40)
        self.assertEqual(element_presentation.note_x, 50)
        self.assertEqual(element_presentation.note_y, 60)
        self.assertEqual(element_presentation.flag_flipped, True)

    def test_element_presentation_deserialization_with_empty_data(self) -> None:
        """Test ElementPresentation deserialization with empty data."""
        data = {}

        element_presentation = ElementPresentation.deserialize(data)

        # Should have default values
        self.assertEqual(element_presentation.sheet, NIL_GUID)
        self.assertEqual(element_presentation.x, 0)
        self.assertEqual(element_presentation.y, 0)
        self.assertEqual(element_presentation.color, CL_BLACK)
        self.assertEqual(element_presentation.size, 1)
        self.assertEqual(element_presentation.width, 1)
        self.assertEqual(element_presentation.text_color, CL_BLACK)
        self.assertEqual(element_presentation.text_size, 7)
        self.assertEqual(element_presentation.font, "Arial")
        self.assertEqual(element_presentation.text_style, 0)
        self.assertEqual(element_presentation.no_text, False)
        self.assertEqual(element_presentation.upside_down_text, False)
        self.assertEqual(element_presentation.flag_flipped, False)


class TestSecundairPresentation(unittest.TestCase):
    """Test SecundairPresentation serialization and deserialization behavior."""

    def setUp(self) -> None:
        """Create fresh dependencies for isolated testing."""
        self.test_guid = Guid(uuid4())

    def test_secundair_presentation_serialize_with_defaults(self) -> None:
        """Test SecundairPresentation serialization with default values."""
        secundair_presentation = SecundairPresentation()

        result = secundair_presentation.serialize()

        # Should include required fields
        self.assertIn(f"Sheet:{encode_guid(NIL_GUID)}", result)
        self.assertIn(f"Color:{CL_BLACK}", result)

        # Should skip default values
        self.assertNotIn("Distance:", result)  # Default 0 should be skipped
        self.assertNotIn("Size:", result)  # Default 1 should be skipped
        self.assertNotIn("Width:", result)  # Default 1 should be skipped
        self.assertNotIn("TextSize:", result)  # Default 7 should be skipped
        self.assertNotIn("TextStyle:", result)  # Default 0 should be skipped
        self.assertNotIn("Otherside:", result)  # Default False should be skipped
        self.assertNotIn("NoText:", result)  # Default False should be skipped
        self.assertNotIn("UpsideDownText:", result)  # Default False should be skipped

    def test_secundair_presentation_serialize_with_full_properties(self) -> None:
        """Test SecundairPresentation serialization with all properties set."""
        secundair_presentation = SecundairPresentation(
            sheet=self.test_guid,
            distance=50,
            otherside=True,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=10,
            strings_y=20,
            note_x=30,
            note_y=40,
        )

        result = secundair_presentation.serialize()

        # Verify all properties are included
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn("Distance:50", result)
        self.assertIn("Otherside:True", result)
        self.assertIn(f"Color:{CL_RED}", result)
        self.assertIn("Size:2", result)
        self.assertIn("Width:3", result)
        self.assertIn(f"TextColor:{CL_BLUE}", result)
        self.assertIn("TextSize:12", result)
        self.assertIn("Font:'Times'", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)
        self.assertIn("StringsX:10", result)
        self.assertIn("StringsY:20", result)
        self.assertIn("NoteX:30", result)
        self.assertIn("NoteY:40", result)

    def test_secundair_presentation_deserialization_works(self) -> None:
        """Test SecundairPresentation deserialization from dictionary data."""
        data = {
            "Sheet": str(self.test_guid),
            "Distance": 50,
            "Otherside": True,
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 12,
            "Font": "Times",
            "TextStyle": 1,
            "NoText": True,
            "UpsideDownText": True,
            "StringsX": 10,
            "StringsY": 20,
            "NoteX": 30,
            "NoteY": 40,
        }

        secundair_presentation = SecundairPresentation.deserialize(data)

        # Verify all properties
        self.assertEqual(secundair_presentation.sheet, self.test_guid)
        self.assertEqual(secundair_presentation.distance, 50)
        self.assertEqual(secundair_presentation.otherside, True)
        self.assertEqual(secundair_presentation.color, CL_RED)
        self.assertEqual(secundair_presentation.size, 2)
        self.assertEqual(secundair_presentation.width, 3)
        self.assertEqual(secundair_presentation.text_color, CL_BLUE)
        self.assertEqual(secundair_presentation.text_size, 12)
        self.assertEqual(secundair_presentation.font, "Times")
        self.assertEqual(secundair_presentation.text_style, 1)
        self.assertEqual(secundair_presentation.no_text, True)
        self.assertEqual(secundair_presentation.upside_down_text, True)
        self.assertEqual(secundair_presentation.strings_x, 10)
        self.assertEqual(secundair_presentation.strings_y, 20)
        self.assertEqual(secundair_presentation.note_x, 30)
        self.assertEqual(secundair_presentation.note_y, 40)

    def test_secundair_presentation_deserialization_with_empty_data(self) -> None:
        """Test SecundairPresentation deserialization with empty data."""
        data = {}

        secundair_presentation = SecundairPresentation.deserialize(data)

        # Should have default values
        self.assertEqual(secundair_presentation.sheet, NIL_GUID)
        self.assertEqual(secundair_presentation.distance, 0)
        self.assertEqual(secundair_presentation.otherside, False)
        self.assertEqual(secundair_presentation.color, CL_BLACK)
        self.assertEqual(secundair_presentation.size, 1)
        self.assertEqual(secundair_presentation.width, 1)
        self.assertEqual(secundair_presentation.text_color, CL_BLACK)
        self.assertEqual(secundair_presentation.text_size, 7)
        self.assertEqual(secundair_presentation.font, "")
        self.assertEqual(secundair_presentation.text_style, 0)
        self.assertEqual(secundair_presentation.no_text, False)
        self.assertEqual(secundair_presentation.upside_down_text, False)
        self.assertEqual(secundair_presentation.strings_x, 0)
        self.assertEqual(secundair_presentation.strings_y, 0)
        self.assertEqual(secundair_presentation.note_x, 0)
        self.assertEqual(secundair_presentation.note_y, 0)

    def test_secundair_presentation_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original = SecundairPresentation(
            sheet=self.test_guid,
            distance=50,
            otherside=True,
            color=CL_RED,
            size=2,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=10,
            strings_y=20,
            note_x=30,
            note_y=40,
        )

        original.serialize()

        # Simulate parsing back from serialized format
        data = {
            "Sheet": str(self.test_guid),
            "Distance": 50,
            "Otherside": True,
            "Color": CL_RED,
            "Size": 2,
            "Width": 3,
            "TextColor": CL_BLUE,
            "TextSize": 12,
            "Font": "Times",
            "TextStyle": 1,
            "NoText": True,
            "UpsideDownText": True,
            "StringsX": 10,
            "StringsY": 20,
            "NoteX": 30,
            "NoteY": 40,
        }

        deserialized = SecundairPresentation.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.sheet, original.sheet)
        self.assertEqual(deserialized.distance, original.distance)
        self.assertEqual(deserialized.otherside, original.otherside)
        self.assertEqual(deserialized.color, original.color)
        self.assertEqual(deserialized.size, original.size)
        self.assertEqual(deserialized.width, original.width)
        self.assertEqual(deserialized.text_color, original.text_color)
        self.assertEqual(deserialized.text_size, original.text_size)
        self.assertEqual(deserialized.font, original.font)
        self.assertEqual(deserialized.text_style, original.text_style)
        self.assertEqual(deserialized.no_text, original.no_text)
        self.assertEqual(deserialized.upside_down_text, original.upside_down_text)
        self.assertEqual(deserialized.strings_x, original.strings_x)
        self.assertEqual(deserialized.strings_y, original.strings_y)
        self.assertEqual(deserialized.note_x, original.note_x)
        self.assertEqual(deserialized.note_y, original.note_y)


if __name__ == "__main__":
    unittest.main()
