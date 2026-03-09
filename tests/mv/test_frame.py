"""Tests for FrameMV class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.color_utils import CL_BLACK, CL_BLUE, CL_RED
from pyptp.elements.element_utils import FrameShape, Guid, LineStyle
from pyptp.elements.mixins import Extra, Geography
from pyptp.elements.mv.frame import FrameMV
from pyptp.network_mv import NetworkMV


class TestFrameMV(unittest.TestCase):
    """Test FrameMV registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkMV()
        self.test_guid = Guid(uuid4())

    def test_frame_registration_works(self) -> None:
        """Verify basic frame registration in network."""
        general = FrameMV.General(guid=self.test_guid, name="Test Frame")
        frame = FrameMV(general=general, presentations=[FrameMV.FramePresentation()])

        # Verify network starts empty
        self.assertEqual(len(self.network.frames), 0)

        # Register frame
        frame.register(self.network)

        # Verify frame was added
        self.assertEqual(len(self.network.frames), 1)
        self.assertEqual(self.network.frames[self.test_guid], frame)

    def test_frame_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = FrameMV.General(guid=self.test_guid, name="Minimal Frame")
        frame = FrameMV(general=general, presentations=[FrameMV.FramePresentation()])

        result = frame.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Minimal Frame'", result)

        # Should not contain optional sections
        self.assertNotIn("#Line", result)
        self.assertNotIn("#Geo", result)
        self.assertNotIn("#Extra", result)

    def test_frame_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = FrameMV.General(
            guid=self.test_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            name="Full Frame",
            revision_date=1234567891,
            image="test_image.png",
            container=True,
            variant=True,
        )

        lines = ["Frame line text"]

        geo_series = [Geography(coordinates=[(100.0, 200.0), (300.0, 400.0)])]

        extras = [Extra(text="key1=value1"), Extra(text="key2=value2")]

        presentation = FrameMV.FramePresentation(
            sheet=self.test_guid,
            sort=FrameShape.ELLIPSE,
            name_x=50,
            name_y=100,
            filled=True,
            fill_color=CL_RED,
            image_size=50,
            color=CL_BLACK,
            width=3,
            style=LineStyle.DASH,
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

        frame = FrameMV(
            general=general,
            lines=lines,
            extras=extras,
            geo_series=geo_series,
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
        self.assertIn("Variant:True", result)

        # Verify line section
        self.assertIn("#Line Text:Frame line text", result)

        # Verify extras sections
        self.assertIn("#Extra Text:key1=value1", result)
        self.assertIn("#Extra Text:key2=value2", result)

        # Verify presentation section
        self.assertIn("#Presentation", result)
        self.assertIn(f"Sheet:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Sort:'Ellipse'", result)
        self.assertIn("NameX:50", result)
        self.assertIn("NameY:100", result)
        self.assertIn("Filled:True", result)
        self.assertIn("NoText:True", result)
        self.assertIn("UpsideDownText:True", result)

    def test_frame_deserialization_works(self) -> None:
        """Test deserialization from VNF format data."""
        data = {
            "general": {
                "GUID": str(self.test_guid),
                "Name": "Deserialized Frame",
                "CreationTime": 1234567890.0,
                "Container": True,
                "Variant": True,
            },
            "lines": [{"Text": "Line text"}],
            "geo_series": [{"Coordinates": "'{(100,0 200,0) (300,0 400,0) }'"}],
            "extras": [
                {"Text": "key1=value1"},
                {"Text": "key2=value2"},
            ],
            "presentations": [
                {
                    "Sheet": str(self.test_guid),
                    "Sort": "Ellipse",
                    "NameX": 50,
                    "NameY": 100,
                    "Filled": True,
                }
            ],
        }

        frame = FrameMV.deserialize(data)

        # Verify general properties
        self.assertEqual(frame.general.guid, self.test_guid)
        self.assertEqual(frame.general.name, "Deserialized Frame")
        self.assertEqual(frame.general.creation_time, 1234567890.0)
        self.assertEqual(frame.general.container, True)
        self.assertEqual(frame.general.variant, True)

        # Verify lines are plain strings
        self.assertEqual(frame.lines, ["Line text"])

        # Verify geo_series
        self.assertEqual(len(frame.geo_series), 1)
        self.assertEqual(
            frame.geo_series[0].coordinates, [(100.0, 200.0), (300.0, 400.0)]
        )

        # Verify extras
        self.assertEqual(len(frame.extras), 2)
        self.assertEqual(frame.extras[0].text, "key1=value1")
        self.assertEqual(frame.extras[1].text, "key2=value2")

        # Verify presentations
        self.assertEqual(len(frame.presentations), 1)
        self.assertEqual(frame.presentations[0].sheet, self.test_guid)
        self.assertEqual(frame.presentations[0].sort, FrameShape.ELLIPSE)
        self.assertEqual(frame.presentations[0].name_x, 50)
        self.assertEqual(frame.presentations[0].name_y, 100)
        self.assertEqual(frame.presentations[0].filled, True)

    def test_frame_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        frame = FrameMV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(frame.general)
        self.assertEqual(frame.general.name, "")
        self.assertEqual(frame.general.creation_time, 0.0)
        self.assertEqual(frame.general.container, False)
        self.assertEqual(frame.general.variant, False)

        # Optional sections should be empty lists
        self.assertEqual(frame.lines, [])
        self.assertEqual(frame.geo_series, [])
        self.assertEqual(frame.extras, [])
        self.assertEqual(frame.presentations, [])

    def test_duplicate_frame_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = FrameMV.General(guid=self.test_guid, name="Frame 1")
        general2 = FrameMV.General(guid=self.test_guid, name="Frame 2")

        frame1 = FrameMV(general=general1, presentations=[FrameMV.FramePresentation()])
        frame2 = FrameMV(general=general2, presentations=[FrameMV.FramePresentation()])

        # Register first frame
        frame1.register(self.network)
        self.assertEqual(self.network.frames[self.test_guid].general.name, "Frame 1")

        # Register second frame with same GUID should overwrite
        frame2.register(self.network)
        self.assertEqual(self.network.frames[self.test_guid].general.name, "Frame 2")

    def test_frame_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = FrameMV.General(guid=self.test_guid, name="Test Frame")

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
        self.assertNotIn("Variant:", result)

    def test_frame_presentation_serialize_with_defaults(self) -> None:
        """Test FramePresentation class serialization with default values."""
        presentation = FrameMV.FramePresentation()

        result = presentation.serialize()

        # Should skip default values (except Sheet which uses no_skip)
        self.assertNotIn("NameX:", result)
        self.assertNotIn("NameY:", result)
        self.assertNotIn("Filled:", result)
        self.assertNotIn("FillColor:", result)
        self.assertNotIn("ImageSize:", result)
        self.assertNotIn("Color:", result)
        self.assertNotIn("Width:", result)
        self.assertNotIn("Style:", result)  # Solid is default
        self.assertNotIn("TextColor:", result)
        self.assertNotIn("TextSize:", result)
        self.assertNotIn("Font:", result)
        self.assertNotIn("TextStyle:", result)
        self.assertNotIn("NoText:", result)
        self.assertNotIn("UpsideDownText:", result)
        self.assertNotIn("StringsX:", result)
        self.assertNotIn("StringsY:", result)
        self.assertNotIn("FirstCorners:", result)

    def test_frame_with_no_lines_serializes_correctly(self) -> None:
        """Test serialization with no lines."""
        general = FrameMV.General(guid=self.test_guid, name="No Lines Frame")
        frame = FrameMV(
            general=general, presentations=[FrameMV.FramePresentation()], lines=[]
        )

        result = frame.serialize()

        self.assertNotIn("#Line", result)

    def test_frame_with_multiple_lines_serializes_correctly(self) -> None:
        """Test serialization with multiple lines."""
        general = FrameMV.General(guid=self.test_guid, name="Multi Line Frame")
        frame = FrameMV(
            general=general,
            presentations=[FrameMV.FramePresentation()],
            lines=["First line", "Second line", "Third line"],
        )

        result = frame.serialize()

        self.assertIn("#Line Text:First line", result)
        self.assertIn("#Line Text:Second line", result)
        self.assertIn("#Line Text:Third line", result)
        # Verify order is preserved
        first_pos = result.index("#Line Text:First line")
        second_pos = result.index("#Line Text:Second line")
        third_pos = result.index("#Line Text:Third line")
        self.assertLess(first_pos, second_pos)
        self.assertLess(second_pos, third_pos)

    def test_frame_with_empty_line_serializes_correctly(self) -> None:
        """Test serialization with empty string line."""
        general = FrameMV.General(guid=self.test_guid, name="Empty Line Frame")
        frame = FrameMV(
            general=general,
            presentations=[FrameMV.FramePresentation()],
            lines=["", "Non-empty line", ""],
        )

        result = frame.serialize()

        # Empty lines should still be serialized
        self.assertIn("#Line Text:", result)
        self.assertIn("#Line Text:Non-empty line", result)
        # Count occurrences of #Line Text:
        line_count = result.count("#Line Text:")
        self.assertEqual(line_count, 3)

    def test_frame_deserialization_with_multiple_lines(self) -> None:
        """Test deserialization with multiple lines."""
        data = {
            "general": {"GUID": str(self.test_guid), "Name": "Multi Line"},
            "lines": [
                {"Text": "Line 1"},
                {"Text": "Line 2"},
                {"Text": "Line 3"},
            ],
        }

        frame = FrameMV.deserialize(data)

        self.assertEqual(len(frame.lines), 3)
        self.assertEqual(frame.lines[0], "Line 1")
        self.assertEqual(frame.lines[1], "Line 2")
        self.assertEqual(frame.lines[2], "Line 3")

    def test_frame_deserialization_with_empty_lines(self) -> None:
        """Test deserialization with empty string lines."""
        data = {
            "general": {"GUID": str(self.test_guid), "Name": "Empty Lines"},
            "lines": [
                {"Text": ""},
                {"Text": "Non-empty"},
                {"Text": ""},
            ],
        }

        frame = FrameMV.deserialize(data)

        self.assertEqual(len(frame.lines), 3)
        self.assertEqual(frame.lines[0], "")
        self.assertEqual(frame.lines[1], "Non-empty")
        self.assertEqual(frame.lines[2], "")

    def test_geography_serialize_with_empty_coordinates(self) -> None:
        """Test Geography class serialization with empty coordinates."""
        geo = Geography()

        result = geo.serialize()

        # Should be empty string for empty coordinates
        self.assertEqual(result, "")

    def test_geography_serialize_with_coordinates(self) -> None:
        """Test Geography class serialization with coordinates."""
        geo = Geography(coordinates=[(1e-9, 23978293.1), (20, 30)])

        result = geo.serialize()

        self.assertEqual(result, "Coordinates:'{(1E-9 23978293.1) (20 30) }'")

    def test_frame_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = FrameMV.General(
            guid=self.test_guid,
            name="Round Trip Frame",
            creation_time=1234567890.0,
            container=True,
        )

        original_frame = FrameMV(
            general=original_general,
            lines=["Round trip text"],
            extras=[Extra(text="key=value")],
            geo_series=[Geography(coordinates=[(100.0, 200.0)])],
            presentations=[
                FrameMV.FramePresentation(sort=FrameShape.ELLIPSE, name_x=50)
            ],
        )

        # Simulate parsing back from VNF format
        data = {
            "general": {
                "GUID": str(self.test_guid),
                "Name": "Round Trip Frame",
                "CreationTime": 1234567890.0,
                "Container": True,
            },
            "lines": [{"Text": "Round trip text"}],
            "extras": [{"Text": "key=value"}],
            "geo_series": [{"Coordinates": "'{(100,0 200,0) }'"}],
            "presentations": [{"Sort": "Ellipse", "NameX": 50}],
        }

        deserialized = FrameMV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_frame.general.guid)
        self.assertEqual(deserialized.general.name, original_frame.general.name)
        self.assertEqual(
            deserialized.general.creation_time, original_frame.general.creation_time
        )
        self.assertEqual(
            deserialized.general.container, original_frame.general.container
        )

        # Verify lines are plain strings
        self.assertEqual(deserialized.lines, ["Round trip text"])

        # Verify extras match
        self.assertEqual(len(deserialized.extras), 1)
        self.assertEqual(deserialized.extras[0].text, "key=value")

        # Verify geo_series
        self.assertEqual(len(deserialized.geo_series), 1)
        self.assertEqual(
            deserialized.geo_series[0].coordinates,
            original_frame.geo_series[0].coordinates,
        )

        self.assertEqual(
            len(deserialized.presentations), len(original_frame.presentations)
        )


if __name__ == "__main__":
    unittest.main()
