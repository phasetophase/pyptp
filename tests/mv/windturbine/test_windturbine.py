"""Tests for TWindTurbineMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.windturbine import WindTurbineMV
from pyptp.network_mv import NetworkMV


class TestWindTurbineRegistration(unittest.TestCase):
    """Test windturbine registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and node for testing."""
        self.network = NetworkMV()

        # Create and register a sheet
        sheet = SheetMV(
            SheetMV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        # Create and register a node for the windturbine
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.windturbine_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_windturbine_registration_works(self) -> None:
        """Test that windturbines can register themselves with the network."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="TestWindTurbine",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        # Verify windturbine is in network
        self.assertIn(self.windturbine_guid, self.network.windturbines)
        self.assertIs(self.network.windturbines[self.windturbine_guid], windturbine)

    def test_windturbine_with_full_properties_serializes_correctly(self) -> None:
        """Test that windturbines with all properties serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullWindTurbine",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            number_of=5,
            wind_speed_or_pref="WindSpeed",
            wind_speed=10.0,
            pref=50.0,
            axis_height=100.0,
            type="TestType",
        )

        presentation = ElementPresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            color=DelphiColor("$FF0000"),
            size=2,
            width=3,
            text_color=DelphiColor("$00FF00"),
            text_size=12,
            font="Arial",
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

        windturbine = WindTurbineMV(
            general,
            [presentation],
            WindTurbineMV.WindTurbineType(),
            None,
            None,
            None,
            None,
            None,
        )
        windturbine.extras.append(Extra(text="foo=bar"))
        windturbine.notes.append(Note(text="Test note"))
        windturbine.register(self.network)

        # Test serialization
        serialized = windturbine.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullWindTurbine'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("NumberOf:5", serialized)
        self.assertIn("WindSpeedOrPref:'WindSpeed'", serialized)
        self.assertIn("WindSpeed:10", serialized)
        self.assertIn("Pref:50", serialized)
        self.assertIn("AxisHeight:100", serialized)
        self.assertIn("WindTurbineType:'TestType'", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a windturbine with the same GUID overwrites the existing one."""
        general1 = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="FirstWindTurbine",
            node=self.node_guid,
        )
        windturbine1 = WindTurbineMV(
            general1,
            [ElementPresentation(sheet=self.sheet_guid)],
            WindTurbineMV.WindTurbineType(),
            None,
            None,
            None,
            None,
            None,
        )
        windturbine1.register(self.network)

        general2 = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="SecondWindTurbine",
            node=self.node_guid,
        )
        windturbine2 = WindTurbineMV(
            general2,
            [ElementPresentation(sheet=self.sheet_guid)],
            WindTurbineMV.WindTurbineType(),
            None,
            None,
            None,
            None,
            None,
        )
        windturbine2.register(self.network)

        # Should only have one windturbine
        self.assertEqual(len(self.network.windturbines), 1)
        # Should be the second windturbine
        self.assertEqual(
            self.network.windturbines[self.windturbine_guid].general.name,
            "SecondWindTurbine",
        )

    def test_minimal_windturbine_serialization(self) -> None:
        """Test that minimal windturbines serialize correctly with only required fields."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="MinimalWindTurbine",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalWindTurbine'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Default values should be included since using no_skip
        self.assertIn("CreationTime:0", serialized)
        self.assertIn("SwitchState:0", serialized)
        self.assertIn("NumberOf:1", serialized)
        self.assertIn("WindSpeedOrPref:'v'", serialized)
        self.assertIn("WindSpeed:14", serialized)
        # Pref:0 should be skipped as default
        self.assertIn("AxisHeight:30", serialized)

    def test_windturbine_with_power_properties_serializes_correctly(self) -> None:
        """Test that windturbines with power properties serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="PowerWindTurbine",
            node=self.node_guid,
            pref=100.0,
            wind_speed=12.0,
            axis_height=80.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()
        self.assertIn("Pref:100", serialized)
        self.assertIn("WindSpeed:12", serialized)
        self.assertIn("AxisHeight:80", serialized)

    def test_windturbine_with_harmonics_serializes_correctly(self) -> None:
        """Test that windturbines with harmonics properties serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="HarmonicsWindTurbine",
            node=self.node_guid,
            type="TestHarmonics",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()
        self.assertIn("WindTurbineType:'TestHarmonics'", serialized)

    def test_windturbine_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that windturbines with maintenance properties serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="MaintenanceWindTurbine",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_windturbine_with_switch_state_serializes_correctly(self) -> None:
        """Test that windturbines with switch state serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="SwitchStateWindTurbine",
            node=self.node_guid,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()
        self.assertIn("SwitchState:1", serialized)

    def test_windturbine_with_field_name_serializes_correctly(self) -> None:
        """Test that windturbines with field name serialize correctly."""
        general = WindTurbineMV.General(
            guid=self.windturbine_guid,
            name="FieldNameWindTurbine",
            node=self.node_guid,
            field_name="TestField",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        windturbine_type = WindTurbineMV.WindTurbineType()
        windturbine = WindTurbineMV(
            general, [presentation], windturbine_type, None, None, None, None, None
        )
        windturbine.register(self.network)

        serialized = windturbine.serialize()
        self.assertIn("FieldName:'TestField'", serialized)


if __name__ == "__main__":
    unittest.main()
