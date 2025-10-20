"""Tests for TAsynchronousGeneratorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestAsynchronousGeneratorRegistration(unittest.TestCase):
    """Test asynchronous generator registration and functionality."""

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

        # Create and register a node for the generator
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.generator_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_async_generator_registration_works(self) -> None:
        """Test that asynchronous generators can register themselves with the network."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="TestGenerator", node=self.node_guid
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        # Verify generator is in network
        self.assertIn(self.generator_guid, self.network.asynchronous_generators)
        self.assertIs(
            self.network.asynchronous_generators[self.generator_guid], generator
        )

    def test_async_generator_with_full_properties_serializes_correctly(self) -> None:
        """Test that asynchronous generators with all properties serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullGenerator",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            pref=50.0,
            earthing=True,
            earthing_resistance=1.5,
            earthing_reactance=2.0,
            type="TestType",
        )

        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType(
            unom=400.0,
            pnom=100.0,
            r_x=0.1,
            istart_inom=5.0,
            poles=4,
            cosnom=0.85,
            p2=0.8,
            cos2=0.9,
            p3=0.6,
            cos3=0.8,
            p4=0.4,
            cos4=0.7,
            p5=0.2,
            starting_torque=1.5,
            critical_speed=1500.0,
            critical_torque=200.0,
            nom_speed=1450.0,
            j=0.1,
            efficiency=0.95,
            k2=1.0,
            k1=0.8,
            k0=0.6,
            double_cage=True,
            own_parameters=True,
            mechanical_torque_speed_characteristic=True,
            electrical_torque_speed_characteristic=True,
            m1=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            m2=[11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0],
            e1=[21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0],
            e2=[31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0],
            rs=0.02,
            xsl=0.05,
            xm=2.0,
            rr=0.015,
            xrl=0.04,
            rr2=0.01,
            xr2l=0.03,
        )

        restriction = AsynchronousGeneratorMV.Restriction(
            sort="TestSort",
            begin_date=20230101,
            end_date=20231231,
            begin_time=8.0,
            end_time=18.0,
            p_max=80.0,
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

        generator = AsynchronousGeneratorMV(
            general, [presentation], generator_type, restriction
        )
        generator.extras.append(Extra("foo=bar"))
        generator.notes.append(Note(text="Test note"))
        generator.register(self.network)

        # Test serialization
        serialized = generator.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#AsynchronousGeneratorType"), 1)
        self.assertEqual(serialized.count("#Restriction"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullGenerator'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:True", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("Pref:50", serialized)
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)
        self.assertIn("AsynchronousGeneratorType:'TestType'", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify type properties
        self.assertIn("Unom:400", serialized)
        self.assertIn("Pnom:100", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:5", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("p2:0.8", serialized)
        self.assertIn("cos2:0.9", serialized)
        self.assertIn("p3:0.6", serialized)
        self.assertIn("cos3:0.8", serialized)
        self.assertIn("p4:0.4", serialized)
        self.assertIn("cos4:0.7", serialized)
        self.assertIn("p5:0.2", serialized)
        self.assertIn("StartingTorque:1.5", serialized)
        self.assertIn("CriticalSpeed:1500", serialized)
        self.assertIn("CriticalTorque:200", serialized)
        self.assertIn("NomSpeed:1450", serialized)
        self.assertIn("J:0.1", serialized)
        self.assertIn("Efficiency:0.95", serialized)
        self.assertIn("K2:1", serialized)
        self.assertIn("K1:0.8", serialized)
        self.assertIn("K0:0.6", serialized)
        self.assertIn("DoubleCage:True", serialized)
        self.assertIn("OwnParameters:True", serialized)
        self.assertIn("MechanicalTorqueSpeedCharacteristic:True", serialized)
        self.assertIn("ElectricalTorqueSpeedCharacteristic:True", serialized)
        self.assertIn("Rs:0.02", serialized)
        self.assertIn("Xsl:0.05", serialized)
        self.assertIn("Xm:2", serialized)
        self.assertIn("Rr:0.015", serialized)
        self.assertIn("Xrl:0.04", serialized)
        self.assertIn("Rr2:0.01", serialized)
        self.assertIn("Xr2l:0.03", serialized)

        # Verify arrays
        self.assertIn("M11:1", serialized)
        self.assertIn("M110:10", serialized)
        self.assertIn("M21:11", serialized)
        self.assertIn("M210:20", serialized)
        self.assertIn("E11:21", serialized)
        self.assertIn("E110:30", serialized)
        self.assertIn("E21:31", serialized)
        self.assertIn("E210:40", serialized)

        # Verify restriction properties
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("BeginTime:8", serialized)
        self.assertIn("EndTime:18", serialized)
        self.assertIn("Pmax:80", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("SymbolStringsX:30", serialized)
        self.assertIn("SymbolStringsY:40", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)
        self.assertIn("FlagFlipped:True", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a generator with the same GUID overwrites the existing one."""
        general1 = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="FirstGenerator", node=self.node_guid
        )
        type1 = AsynchronousGeneratorMV.ASynchronousGeneratorType(pnom=50.0)
        generator1 = AsynchronousGeneratorMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], type1
        )
        generator1.register(self.network)

        general2 = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="SecondGenerator", node=self.node_guid
        )
        type2 = AsynchronousGeneratorMV.ASynchronousGeneratorType(pnom=100.0)
        generator2 = AsynchronousGeneratorMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], type2
        )
        generator2.register(self.network)

        # Should only have one generator
        self.assertEqual(len(self.network.asynchronous_generators), 1)
        # Should be the second generator
        self.assertEqual(
            self.network.asynchronous_generators[self.generator_guid].general.name,
            "SecondGenerator",
        )

    def test_minimal_async_generator_serialization(self) -> None:
        """Test that minimal asynchronous generators serialize correctly with only required fields."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="MinimalGenerator", node=self.node_guid
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#AsynchronousGeneratorType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalGenerator'", serialized)

        # Should not have optional sections
        self.assertNotIn("#Restriction", serialized)

    def test_async_generator_with_earthing_serializes_correctly(self) -> None:
        """Test that asynchronous generators with earthing serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="EarthingGenerator",
            node=self.node_guid,
            earthing=True,
            earthing_resistance=1.5,
            earthing_reactance=2.0,
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)

    def test_async_generator_with_power_reference_serializes_correctly(self) -> None:
        """Test that asynchronous generators with power reference serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="PowerRefGenerator",
            node=self.node_guid,
            pref=50.0,
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("Pref:50", serialized)

    def test_async_generator_with_type_properties_serializes_correctly(self) -> None:
        """Test that asynchronous generators with type properties serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="TypeGenerator", node=self.node_guid
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType(
            unom=400.0,
            pnom=100.0,
            r_x=0.1,
            istart_inom=5.0,
            poles=4,
            cosnom=0.85,
            efficiency=0.95,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("Unom:400", serialized)
        self.assertIn("Pnom:100", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:5", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("Efficiency:0.95", serialized)

    def test_async_generator_with_maintenance_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that asynchronous generators with maintenance properties serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="MaintenanceGenerator",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_async_generator_with_switch_state_serializes_correctly(self) -> None:
        """Test that asynchronous generators with switch state serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="SwitchStateGenerator",
            node=self.node_guid,
            switch_state=True,
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("SwitchState:True", serialized)

    def test_async_generator_with_field_name_serializes_correctly(self) -> None:
        """Test that asynchronous generators with field name serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="FieldNameGenerator",
            node=self.node_guid,
            field_name="TestField",
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("FieldName:'TestField'", serialized)

    def test_async_generator_with_not_preferred_serializes_correctly(self) -> None:
        """Test that asynchronous generators with not preferred flag serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid,
            name="NotPreferredGenerator",
            node=self.node_guid,
            not_preferred=True,
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(general, [presentation], generator_type)
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("NotPreferred:True", serialized)

    def test_async_generator_with_restriction_serializes_correctly(self) -> None:
        """Test that asynchronous generators with restriction serialize correctly."""
        general = AsynchronousGeneratorMV.General(
            guid=self.generator_guid, name="RestrictedGenerator", node=self.node_guid
        )
        generator_type = AsynchronousGeneratorMV.ASynchronousGeneratorType()
        restriction = AsynchronousGeneratorMV.Restriction(
            sort="TestSort",
            begin_date=20230101,
            end_date=20231231,
            begin_time=8.0,
            end_time=18.0,
            p_max=80.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorMV(
            general, [presentation], generator_type, restriction
        )
        generator.register(self.network)

        serialized = generator.serialize()
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("BeginTime:8", serialized)
        self.assertIn("EndTime:18", serialized)
        self.assertIn("Pmax:80", serialized)


if __name__ == "__main__":
    unittest.main()
