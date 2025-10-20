"""Tests for TFrameLS class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.color_utils import CL_BLACK, CL_BLUE, CL_RED
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.frame import FrameLV
from pyptp.elements.lv.shared import Text
from pyptp.elements.mixins import Extra
from pyptp.network_lv import NetworkLV


class TestTFrameLS(unittest.TestCase):
    """Test TFrameLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())

    def test_frame_registration_works(self) -> None:
        """Verify basic frame registration in network."""
        general = FrameLV.General(guid=self.test_guid, name="Test Frame")
        frame = FrameLV(
            general=general, line=None, extras=None, geo=None, presentations=[]
        )

        # Verify network starts empty
        self.assertEqual(len(self.network.frames), 0)

        # Register frame
        frame.register(self.network)

        # Verify frame was added
        self.assertEqual(len(self.network.frames), 1)
        self.assertEqual(self.network.frames[self.test_guid], frame)

    def test_frame_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = FrameLV.General(guid=self.test_guid, name="Minimal Frame")
        frame = FrameLV(
            general=general, line=None, extras=None, geo=None, presentations=[]
        )

        result = frame.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Minimal Frame'", result)

        # Should not contain optional sections
        self.assertNotIn("#Line", result)
        self.assertNotIn("#Geo", result)
        self.assertNotIn("#Extra", result)
        # May contain empty #Presentation sections due to empty list

    def test_frame_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = FrameLV.General(
            guid=self.test_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            name="Full Frame",
            revision_date=1234567891.0,
            image="test_image.png",
            container=True,
        )

        line = Text(text="Frame line text")

        geo = FrameLV.Geography(coordinates=[(100.0, 200.0), (300.0, 400.0)])

        extras = [Extra(text="key1=value1"), Extra(text="key2=value2")]

        presentation = FrameLV.FramePresentation(
            sheet=self.test_guid,
            sort="Circle",
            name_x=50,
            name_y=100,
            filled=True,
            fill_color=CL_RED,
            image_size=2,
            color=CL_BLACK,
            width=3,
            text_color=CL_BLUE,
            text_size=12,
            font="Times New Roman",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=25,
            strings_y=75,
            first_corners=[(10, 20), (30, 40)],
        )

        frame = FrameLV(
            general=general,
            line=line,
            extras=extras,
            geo=geo,
            presentations=[presentation],
        )

        result = frame.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("CreationTime:1234567890.5", result)
        self.assertIn("MutationDate:20240101", result)
        self.assertIn("Name:'Full Frame'", result)
        self.assertIn("RevisionDate:1234567891", result)
        self.assertIn("Image:'test_image.png'", result)
        self.assertIn("Container:True", result)

        # Verify line section
        self.assertIn("#Line", result)
        self.assertIn("{'Text': 'Frame line text'}", result)

        # Verify geo section
        self.assertIn("#Geo", result)
        self.assertIn("Coordinates:'{(100,0 200,0) (300,0 400,0) }'", result)

        # Verify extras sections
        self.assertIn("#Extra {'Text': 'key1=value1'}", result)
        self.assertIn("#Extra {'Text': 'key2=value2'}", result)

        # Verify presentation section
        self.assertIn("#Presentation", result)
        self.assertIn(f"Sheet:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Sort:'Circle'", result)
        self.assertIn("NameX:50", result)
        self.assertIn("NameY:100", result)
        self.assertIn("Filled:True", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)

    def test_frame_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Deserialized Frame",
                    "CreationTime": 1234567890.0,
                    "Container": True,
                }
            ],
            "line": [{"text": "Line text"}],
            "geo": [{"Coordinates": "'{(100,0 200,0) (300,0 400,0) }'"}],
            "extras": [
                {"key": "key1", "value": "value1"},
                {"key": "key2", "value": "value2"},
            ],
            "presentations": [
                {
                    "Sheet": str(self.test_guid),
                    "Sort": "Circle",
                    "NameX": 50,
                    "NameY": 100,
                    "Filled": True,
                }
            ],
        }

        frame = FrameLV.deserialize(data)

        # Verify general properties
        self.assertEqual(frame.general.guid, self.test_guid)
        self.assertEqual(frame.general.name, "Deserialized Frame")
        self.assertEqual(frame.general.creation_time, 1234567890.0)
        self.assertEqual(frame.general.container, True)

        # Verify line
        self.assertIsNotNone(frame.line)
        if frame.line:
            self.assertEqual(frame.line.text, "Line text")

        # Verify geo
        self.assertIsNotNone(frame.geo)
        if frame.geo:
            self.assertEqual(frame.geo.coordinates, [(100.0, 200.0), (300.0, 400.0)])

        # Verify extras
        self.assertIsNotNone(frame.extras)

        # Verify presentations
        self.assertEqual(len(frame.presentations), 1)
        self.assertEqual(frame.presentations[0].sheet, self.test_guid)
        self.assertEqual(frame.presentations[0].sort, "Circle")
        self.assertEqual(frame.presentations[0].name_x, 50)
        self.assertEqual(frame.presentations[0].name_y, 100)
        self.assertEqual(frame.presentations[0].filled, True)

    def test_frame_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        frame = FrameLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(frame.general)
        self.assertEqual(frame.general.name, "")
        self.assertEqual(frame.general.creation_time, 0)
        self.assertEqual(frame.general.container, False)

        # Optional sections should be None or empty
        self.assertIsNone(frame.line)
        self.assertIsNone(frame.geo)
        self.assertIsNone(frame.extras)
        self.assertEqual(len(frame.presentations), 0)

    def test_duplicate_frame_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = FrameLV.General(guid=self.test_guid, name="Frame 1")
        general2 = FrameLV.General(guid=self.test_guid, name="Frame 2")

        frame1 = FrameLV(
            general=general1, line=None, extras=None, geo=None, presentations=[]
        )
        frame2 = FrameLV(
            general=general2, line=None, extras=None, geo=None, presentations=[]
        )

        # Register first frame
        frame1.register(self.network)
        self.assertEqual(self.network.frames[self.test_guid].general.name, "Frame 1")

        # Register second frame with same GUID should overwrite
        frame2.register(self.network)
        # Verify frame was overwritten
        self.assertEqual(self.network.frames[self.test_guid].general.name, "Frame 2")

    def test_frame_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = FrameLV.General(guid=self.test_guid, name="Test Frame")

        result = general.serialize()

        # Should include required fields
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Test Frame'", result)

        # CreationTime uses no_skip so it always appears
        self.assertIn("CreationTime:", result)
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("Image:", result)
        self.assertNotIn("Container:", result)

    def test_frame_presentation_serialize_with_defaults(self) -> None:
        """Test FramePresentation class serialization with default values."""
        presentation = FrameLV.FramePresentation()

        result = presentation.serialize()

        # Should skip default values
        self.assertNotIn("Sheet:", result)
        self.assertNotIn("Sort:", result)  # Rectangle is default
        self.assertNotIn("NameX:", result)
        self.assertNotIn("NameY:", result)
        self.assertNotIn("Filled:", result)
        self.assertNotIn("FillColor:", result)
        self.assertNotIn("ImageSize:", result)
        self.assertNotIn("Color:", result)
        self.assertNotIn("Width:", result)
        self.assertNotIn("TextColor:", result)
        self.assertNotIn("TextSize:", result)
        self.assertNotIn("Font:", result)
        self.assertNotIn("TextStyle:", result)
        self.assertNotIn("NoText:", result)
        self.assertNotIn("UpsideDownText:", result)
        self.assertNotIn("StringsX:", result)
        self.assertNotIn("StringsY:", result)
        self.assertNotIn("FirstCorners:", result)

    def test_frame_geography_serialize_with_empty_coordinates(self) -> None:
        """Test Geography class serialization with empty coordinates."""
        geo = FrameLV.Geography()

        result = geo.serialize()

        # Should be empty string for empty coordinates
        self.assertEqual(result, "")

    def test_frame_geography_serialize_with_coordinates(self) -> None:
        """Test Geography class serialization with coordinates."""
        geo = FrameLV.Geography(coordinates=[(100.0, 200.0), (300.0, 400.0)])

        result = geo.serialize()

        self.assertEqual(result, "Coordinates:'{(100,0 200,0) (300,0 400,0) }'")

    def test_frame_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = FrameLV.General(
            guid=self.test_guid,
            name="Round Trip Frame",
            creation_time=1234567890.0,
            container=True,
        )

        original_frame = FrameLV(
            general=original_general,
            line=Text(text="Round trip text"),
            extras=[Extra(text="key=value")],
            geo=FrameLV.Geography(coordinates=[(100.0, 200.0)]),
            presentations=[FrameLV.FramePresentation(sort="Circle", name_x=50)],
        )

        original_frame.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Round Trip Frame",
                    "CreationTime": 1234567890.0,
                    "Container": True,
                }
            ],
            "line": [{"text": "Round trip text"}],
            "extras": [{"key": "key", "value": "value"}],
            "geo": [{"Coordinates": "'{(100,0 200,0) }'"}],
            "presentations": [{"Sort": "Circle", "NameX": 50}],
        }

        deserialized = FrameLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_frame.general.guid)
        self.assertEqual(deserialized.general.name, original_frame.general.name)
        self.assertEqual(
            deserialized.general.creation_time, original_frame.general.creation_time
        )
        self.assertEqual(
            deserialized.general.container, original_frame.general.container
        )

        # Verify line
        self.assertIsNotNone(deserialized.line)
        self.assertIsNotNone(original_frame.line)
        if deserialized.line and original_frame.line:
            self.assertEqual(deserialized.line.text, original_frame.line.text)

        # Verify extras
        self.assertIsNotNone(deserialized.extras)
        self.assertIsNotNone(original_frame.extras)
        if deserialized.extras and original_frame.extras:
            self.assertEqual(len(deserialized.extras), len(original_frame.extras))

        # Verify geo
        self.assertIsNotNone(deserialized.geo)
        self.assertIsNotNone(original_frame.geo)
        if deserialized.geo and original_frame.geo:
            self.assertEqual(
                deserialized.geo.coordinates, original_frame.geo.coordinates
            )

        self.assertEqual(
            len(deserialized.presentations), len(original_frame.presentations)
        )


if __name__ == "__main__":
    unittest.main()
