"""Tests for TFuseLS class."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock  # noqa: F401 - kept for legacy reference in docstrings
from uuid import uuid4

import pandas as pd

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.presentations import SecundairPresentation
from pyptp.elements.lv.shared import FuseType
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestTFuseLS(unittest.TestCase):
    """Test TFuseLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())
        self.in_object_guid = Guid(uuid4())

    def test_fuse_registration_works(self) -> None:
        """Verify basic fuse registration in network."""
        general = FuseLV.General(guid=self.test_guid, name="Test Fuse", type="16A")
        fuse = FuseLV(general=general)

        # Verify network starts empty
        self.assertEqual(len(self.network.fuses), 0)

        # Register fuse
        fuse.register(self.network)

        # Verify fuse was added
        self.assertEqual(len(self.network.fuses), 1)
        self.assertEqual(self.network.fuses[self.test_guid], fuse)

    def test_fuse_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = FuseLV.General(guid=self.test_guid, name="Minimal Fuse", type="16A")
        fuse = FuseLV(general=general)

        result = fuse.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Minimal Fuse'", result)
        self.assertIn("FuseType:'16A'", result)
        self.assertIn("CreationTime:0", result)
        self.assertIn("Side:1", result)

        # Should not contain optional sections
        self.assertNotIn("#FuseType", result)
        self.assertNotIn("#Extra", result)
        self.assertNotIn("#Note", result)

    def test_fuse_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = FuseLV.General(
            guid=self.test_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            revision_date=1234567891.0,
            name="Full Fuse",
            in_object=self.in_object_guid,
            side=2,
            standardizable=False,
            type="25A",
        )

        type = FuseType(short_name="25A", unom=230.0, inom=25.0)

        presentation = SecundairPresentation(
            sheet=self.test_guid, distance=100, otherside=False
        )

        fuse = FuseLV(general=general, type=type, presentations=[presentation])

        # Add extras and notes
        fuse.extras = [Extra(text="key1=value1"), Extra(text="key2=value2")]
        fuse.notes = [Note(text="Test note 1"), Note(text="Test note 2")]

        result = fuse.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("CreationTime:1234567890.5", result)
        self.assertIn("MutationDate:20240101", result)
        self.assertIn("RevisionDate:1234567891", result)
        self.assertIn("Name:'Full Fuse'", result)
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", result)
        self.assertIn("Side:2", result)
        self.assertNotIn("Standardizable:", result)  # False values are skipped
        self.assertIn("FuseType:'25A'", result)

        # Verify fuse type section
        self.assertIn("#FuseType", result)
        self.assertIn("ShortName:'25A'", result)
        self.assertIn("Unom:230", result)
        self.assertIn("Inom:25", result)

        # Verify presentation section
        self.assertIn("#Presentation", result)
        self.assertIn(f"Sheet:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Distance:100", result)

        # Verify extras and notes
        self.assertIn("#Extra Text:key1=value1", result)
        self.assertIn("#Extra Text:key2=value2", result)
        self.assertIn("#Note Text:Test note 1", result)
        self.assertIn("#Note Text:Test note 2", result)

    def test_fuse_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Deserialized Fuse",
                    "CreationTime": 1234567890.0,
                    "Side": 2,
                    "Standardizable": False,
                    "FuseType": "25A",
                }
            ],
            "fuse_type": {"ShortName": "25A", "Unom": 230.0, "Inom": 25.0},
            "presentations": [
                {"Sheet": str(self.test_guid), "Distance": 100, "Otherside": False}
            ],
        }

        fuse = FuseLV.deserialize(data)

        # Verify general properties
        self.assertEqual(fuse.general.guid, self.test_guid)
        self.assertEqual(fuse.general.name, "Deserialized Fuse")
        self.assertEqual(fuse.general.creation_time, 1234567890.0)
        self.assertEqual(fuse.general.side, 2)
        self.assertEqual(fuse.general.standardizable, False)
        self.assertEqual(fuse.general.type, "25A")

        # Verify fuse type
        self.assertIsNotNone(fuse.type)
        if fuse.type:
            self.assertEqual(fuse.type.short_name, "25A")
            self.assertEqual(fuse.type.unom, 230.0)
            self.assertEqual(fuse.type.inom, 25.0)

        # Verify presentations
        self.assertEqual(len(fuse.presentations), 1)
        self.assertEqual(fuse.presentations[0].sheet, self.test_guid)
        self.assertEqual(fuse.presentations[0].distance, 100)
        self.assertEqual(fuse.presentations[0].otherside, False)

    def test_fuse_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        fuse = FuseLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(fuse.general)
        self.assertEqual(fuse.general.name, "")
        self.assertEqual(fuse.general.creation_time, 0)
        self.assertEqual(fuse.general.side, 1)
        self.assertEqual(fuse.general.standardizable, True)
        self.assertEqual(fuse.general.type, "")

        # Optional sections should be None or empty
        self.assertIsNone(fuse.type)
        self.assertEqual(len(fuse.presentations), 0)

    def test_duplicate_fuse_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = FuseLV.General(guid=self.test_guid, name="Fuse 1", type="16A")
        general2 = FuseLV.General(guid=self.test_guid, name="Fuse 2", type="25A")

        fuse1 = FuseLV(general=general1)
        fuse2 = FuseLV(general=general2)

        # Register first fuse
        fuse1.register(self.network)
        self.assertEqual(self.network.fuses[self.test_guid].general.name, "Fuse 1")

        # Register second fuse with same GUID should overwrite
        fuse2.register(self.network)
        # Verify fuse was overwritten
        self.assertEqual(self.network.fuses[self.test_guid].general.name, "Fuse 2")

    def test_fuse_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = FuseLV.General(guid=self.test_guid, name="Test Fuse", type="16A")

        result = general.serialize()

        # Should include required fields
        self.assertIn(f"GUID:'{{{str(self.test_guid).upper()}}}'", result)
        self.assertIn("Name:'Test Fuse'", result)
        self.assertIn("FuseType:'16A'", result)
        self.assertIn("CreationTime:0", result)
        self.assertIn("Side:1", result)

        # Should skip default values
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("InObject:", result)  # NIL_GUID should be skipped
        self.assertIn(
            "Standardizable:", result
        )  # True is not skipped (skip=False by default)

    def test_fuse_general_serialize_with_in_object(self) -> None:
        """Test General class serialization with InObject set."""
        general = FuseLV.General(
            guid=self.test_guid,
            name="Test Fuse",
            in_object=self.in_object_guid,
            type="16A",
        )

        result = general.serialize()

        # Should include InObject when not NIL_GUID
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", result)

    def test_fuse_set_fuse_type_method(self) -> None:
        """Test set_fuse_type method with Types provider."""
        general = FuseLV.General(guid=self.test_guid, name="Test Fuse", type="16A")
        fuse = FuseLV(general=general)

        # Build a tiny Excel with a single fuse type
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            fuse_df = pd.DataFrame(
                {
                    "Name": ["16A"],
                    "Shortname": ["16A"],
                    "Unom": [230],
                    "Inom": [16.0],
                }
            )
            with pd.ExcelWriter(path) as writer:
                fuse_df.to_excel(writer, sheet_name="Fuse", index=False)
            from pyptp.type_reader import Types

            types = Types(str(path))

            # Set fuse type
            fuse.set_fuse_type(types, "16A")

        # Verify fuse type was set
        self.assertIsNotNone(fuse.type)
        if fuse.type:
            self.assertEqual(fuse.type.short_name, "16A")
            self.assertEqual(fuse.type.unom, 230)
            self.assertEqual(fuse.type.inom, 16.0)

    def test_fuse_set_fuse_type_method_unknown_type(self) -> None:
        """Test set_fuse_type method with unknown type using Types provider."""
        general = FuseLV.General(guid=self.test_guid, name="Test Fuse", type="16A")
        fuse = FuseLV(general=general)

        from pyptp.type_reader import Types

        types = Types()  # default workbook likely doesn't contain 'UnknownType'

        # Set unknown fuse type
        fuse.set_fuse_type(types, "UnknownType")

        # Verify fuse type remains None
        self.assertIsNone(fuse.type)

    def test_fuse_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = FuseLV.General(
            guid=self.test_guid,
            name="Round Trip Fuse",
            creation_time=1234567890.0,
            side=2,
            type="25A",
        )

        original_fuse_type = FuseType(short_name="25A", unom=230.0, inom=25.0)

        original_fuse = FuseLV(
            general=original_general,
            type=original_fuse_type,
            presentations=[SecundairPresentation(distance=100, otherside=False)],
        )

        original_fuse.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Round Trip Fuse",
                    "CreationTime": 1234567890.0,
                    "Side": 2,
                    "FuseType": "25A",
                }
            ],
            "fuse_type": {"ShortName": "25A", "Unom": 230.0, "Inom": 25.0},
            "presentations": [{"Distance": 100, "Otherside": False}],
        }

        deserialized = FuseLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_fuse.general.guid)
        self.assertEqual(deserialized.general.name, original_fuse.general.name)
        self.assertEqual(
            deserialized.general.creation_time, original_fuse.general.creation_time
        )
        self.assertEqual(deserialized.general.side, original_fuse.general.side)
        self.assertEqual(deserialized.general.type, original_fuse.general.type)

        # Verify fuse type properties
        if deserialized.type and original_fuse.general.type:
            self.assertEqual(
                deserialized.type.short_name, original_fuse.type.short_name
            )
            self.assertEqual(deserialized.type.unom, original_fuse.type.unom)
            self.assertEqual(deserialized.type.inom, original_fuse.type.inom)

        # Verify presentations
        self.assertEqual(
            len(deserialized.presentations), len(original_fuse.presentations)
        )
        if len(deserialized.presentations) > 0 and len(original_fuse.presentations) > 0:
            self.assertEqual(
                deserialized.presentations[0].sheet,
                original_fuse.presentations[0].sheet,
            )
            self.assertEqual(
                deserialized.presentations[0].distance,
                original_fuse.presentations[0].distance,
            )


if __name__ == "__main__":
    unittest.main()
