"""Tests for TSpecialTransformerLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestSpecialTransformerRegistration(unittest.TestCase):
    """Test special transformer registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
        self.network = NetworkLV()

        # Create and register a sheet
        sheet = SheetLV(
            SheetLV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        # Create and register nodes
        node1 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="Node1"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("b8b53fef-12b8-4c98-96f2-0da060b51000")), name="Node2"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.special_transformer_guid = Guid(
            UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c")
        )

    def test_special_transformer_registration_works(self) -> None:
        """Test that special transformers can register themselves with the network."""
        general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="TestSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            short_name="TestType"
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer = SpecialTransformerLV(
            general, [presentation], special_transformer_type
        )
        special_transformer.register(self.network)

        # Verify special transformer is in network
        self.assertIn(self.special_transformer_guid, self.network.special_transformers)
        self.assertIs(
            self.network.special_transformers[self.special_transformer_guid],
            special_transformer,
        )

    def test_special_transformer_with_full_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that special transformers with all properties serialize correctly."""
        general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            revision_date=1234567891.0,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullSpecialTransformer",
            switch_state1_L1=False,
            switch_state1_L2=True,
            switch_state1_L3=False,
            switch_state1_N=True,
            switch_state1_PE=False,
            switch_state2_L1=True,
            switch_state2_L2=False,
            switch_state2_L3=True,
            switch_state2_N=False,
            switch_state2_PE=True,
            field_name1="Field1",
            field_name2="Field2",
            failure_frequency=0.01,
            type="TestSpecialTransformerType",
            switch_state_N_PE=True,
            switch_state_PE_e=True,
            re=5.0,
            tap_position=1.5,
        )

        special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            sort=1,
            short_name="TestSpecialTransformerType",
            snom=1000.0,
            unom1=10.0,
            unom2=0.4,
            ukmin=6.0,
            uknom=6.5,
            ukmax=7.0,
            pkmin=5.0,
            pknom=5.5,
            pkmax=6.0,
            po=1.0,
            io=0.1,
            R0=0.1,
            Z0=0.2,
            R0URo_min=1,
            R0URo_nom=2,
            R0URo_max=3,
            Z0URo_min=4,
            Z0URo_nom=5,
            Z0URo_max=6,
            R0URk_min=7,
            R0URk_nom=8,
            R0URk_max=9,
            Z0URk_min=10,
            Z0URk_nom=11,
            Z0URk_max=12,
            R0RUk_min=13,
            R0RUk_nom=14,
            R0RUk_max=15,
            Z0RUk_min=16,
            Z0RUk_nom=17,
            Z0RUk_max=18,
            ik2s=10.0,
            tap_side=1,
            tap_size=2.5,
            tap_min=-5,
            tap_nom=0,
            tap_max=5,
        )

        voltage_control = SpecialTransformerLV.VoltageControl(
            present=True,
            status=1,
            measure_side=1,
            setpoint=0.38,
            deadband=0.02,
            control_sort=1,
            Rc=0.1,
            Xc=0.2,
            compounding_at_generation=False,
            pmin1=10,
            umin1=0.35,
            pmax1=100,
            umax1=0.42,
        )

        presentation = BranchPresentation(
            sheet=self.sheet_guid,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=12,
            font="Arial",
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
            flag_flipped2=False,
        )

        special_transformer = SpecialTransformerLV(
            general, [presentation], special_transformer_type, voltage_control
        )
        special_transformer.extras.append(Extra(text="foo=bar"))
        special_transformer.notes.append(Note(text="Test note"))
        special_transformer.register(self.network)

        # Test serialization
        serialized = special_transformer.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#SpecialTransformerType", serialized)
        self.assertIn("#VoltageControl", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullSpecialTransformer'", serialized)
        self.assertIn("CreationTime:1234567890.5", serialized)
        self.assertIn("MutationDate:20240101", serialized)
        self.assertIn("RevisionDate:1234567891", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("SpecialTransformerType:'TestSpecialTransformerType'", serialized)
        self.assertIn("SwitchState_N_PE:True", serialized)
        self.assertIn("SwitchState_PE_e:True", serialized)
        self.assertIn("Re:5.0", serialized)
        self.assertIn("TapPosition:1.5", serialized)
        self.assertNotIn("SwitchState1_L1:", serialized)  # False values are skipped
        # SwitchState1_L2 was set to True, but skip=True means it's skipped when True
        # SwitchState2_PE was set to True, but skip=True means it's skipped when True

        # Verify special transformer type properties
        self.assertIn("Sort:1", serialized)
        self.assertIn("ShortName:'TestSpecialTransformerType'", serialized)
        self.assertIn("Snom:1000.0", serialized)
        self.assertIn("Unom1:10.0", serialized)
        self.assertIn("Unom2:0.4", serialized)
        self.assertIn("Ukmin:6.0", serialized)
        self.assertIn("Uknom:6.5", serialized)
        self.assertIn("Ukmax:7.0", serialized)
        self.assertIn("Pkmin:5.0", serialized)
        self.assertIn("Pknom:5.5", serialized)
        self.assertIn("Pkmax:6.0", serialized)
        self.assertIn("Po:1.0", serialized)
        self.assertIn("Io:0.1", serialized)
        self.assertIn("R0:0.1", serialized)
        self.assertIn("Z0:0.2", serialized)
        self.assertIn("R0URomin:1", serialized)
        self.assertIn("R0URonom:2", serialized)
        self.assertIn("R0URomax:3", serialized)
        self.assertIn("Z0URomin:4", serialized)
        self.assertIn("Z0URonom:5", serialized)
        self.assertIn("Z0URomax:6", serialized)
        self.assertIn("R0URkmin:7", serialized)
        self.assertIn("R0URknom:8", serialized)
        self.assertIn("R0URkmax:9", serialized)
        self.assertIn("Z0URkmin:10", serialized)
        self.assertIn("Z0URknom:11", serialized)
        self.assertIn("Z0URkmax:12", serialized)
        self.assertIn("R0RUkmin:13", serialized)
        self.assertIn("R0RUknom:14", serialized)
        self.assertIn("R0RUkmax:15", serialized)
        self.assertIn("Z0RUkmin:16", serialized)
        self.assertIn("Z0RUknom:17", serialized)
        self.assertIn("Z0RUkmax:18", serialized)
        self.assertIn("Ik2s:10.0", serialized)
        self.assertIn("TapSide:1", serialized)
        self.assertIn("TapSize:2.5", serialized)
        self.assertIn("TapMin:-5", serialized)
        # TapNom:0 is skipped when 0 (default)
        self.assertIn("TapMax:5", serialized)

        # Verify voltage control properties
        self.assertIn("Present:True", serialized)
        self.assertIn("Status:1", serialized)
        self.assertIn("MeasureSide:1", serialized)
        self.assertIn("Setpoint:0.38", serialized)
        self.assertIn("Deadband:0.02", serialized)
        self.assertIn("ControlSort:1", serialized)
        self.assertIn("Rc:0.1", serialized)
        self.assertIn("Xc:0.2", serialized)
        self.assertNotIn(
            "CompoundingAtGeneration:", serialized
        )  # False values are skipped
        self.assertIn("Pmin1:10", serialized)
        self.assertIn("Umin1:0.35", serialized)
        self.assertIn("Pmax1:100", serialized)
        self.assertIn("Umax1:0.42", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("Strings2X:30", serialized)
        self.assertIn("Strings2Y:40", serialized)
        self.assertIn("MidStringsX:50", serialized)
        self.assertIn("MidStringsY:60", serialized)
        self.assertIn("FaultStringsX:70", serialized)
        self.assertIn("FaultStringsY:80", serialized)
        self.assertIn("NoteX:90", serialized)
        self.assertIn("NoteY:100", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_special_transformer_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.special_transformer_guid),
                    "Name": "Deserialized Special Transformer",
                    "CreationTime": 1234567890.0,
                    "Node1": str(self.node1_guid),
                    "Node2": str(self.node2_guid),
                    "SwitchState1_L1": False,
                    "SwitchState1_L2": True,
                    "SpecialTransformerType": "TestType",
                    "TapPosition": 1.5,
                }
            ],
            "specialTransformerType": [
                {
                    "ShortName": "TestType",
                    "Snom": 1000.0,
                    "Unom1": 10.0,
                    "Unom2": 0.4,
                    "Uknom": 6.5,
                    "Ik2s": 10.0,
                }
            ],
            "voltageControl": [
                {
                    "Present": True,
                    "Status": 1,
                    "MeasureSide": 1,
                    "Setpoint": 0.38,
                }
            ],
            "presentations": [{"Sheet": str(self.sheet_guid)}],
        }

        special_transformer = SpecialTransformerLV.deserialize(data)

        # Verify general properties
        self.assertEqual(
            special_transformer.general.guid, self.special_transformer_guid
        )
        self.assertEqual(
            special_transformer.general.name, "Deserialized Special Transformer"
        )
        self.assertEqual(special_transformer.general.creation_time, 1234567890.0)
        self.assertEqual(special_transformer.general.node1, self.node1_guid)
        self.assertEqual(special_transformer.general.node2, self.node2_guid)
        self.assertEqual(special_transformer.general.switch_state1_L1, False)
        self.assertEqual(special_transformer.general.switch_state1_L2, True)
        self.assertEqual(special_transformer.general.type, "TestType")
        self.assertEqual(special_transformer.general.tap_position, 1.5)

        # Verify special transformer type
        self.assertIsNotNone(special_transformer.type)
        self.assertEqual(special_transformer.type.short_name, "TestType")
        self.assertEqual(special_transformer.type.snom, 1000.0)
        self.assertEqual(special_transformer.type.unom1, 10.0)
        self.assertEqual(special_transformer.type.unom2, 0.4)
        self.assertEqual(special_transformer.type.uknom, 6.5)
        self.assertEqual(special_transformer.type.ik2s, 10.0)

        # Verify voltage control
        self.assertIsNotNone(special_transformer.voltage_control)
        if special_transformer.voltage_control:
            self.assertEqual(special_transformer.voltage_control.present, True)
            self.assertEqual(special_transformer.voltage_control.status, 1)
            self.assertEqual(special_transformer.voltage_control.measure_side, 1)
            self.assertEqual(special_transformer.voltage_control.setpoint, 0.38)

        # Verify presentations
        self.assertEqual(len(special_transformer.presentations), 1)
        self.assertEqual(special_transformer.presentations[0].sheet, self.sheet_guid)

    def test_special_transformer_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        special_transformer = SpecialTransformerLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(special_transformer.general)
        self.assertEqual(special_transformer.general.name, "")
        self.assertEqual(special_transformer.general.creation_time, 0)
        self.assertEqual(special_transformer.general.switch_state1_L1, True)
        self.assertEqual(special_transformer.general.switch_state1_L2, True)
        self.assertEqual(special_transformer.general.type, "")
        self.assertEqual(special_transformer.general.tap_position, 0)

        # Should have default special transformer type
        self.assertIsNotNone(special_transformer.type)
        self.assertEqual(special_transformer.type.short_name, "")
        self.assertEqual(special_transformer.type.snom, 0)
        self.assertEqual(special_transformer.type.sort, 4)

        # Voltage control should be None
        self.assertIsNone(special_transformer.voltage_control)

        # Presentations should be empty
        self.assertEqual(len(special_transformer.presentations), 0)

    def test_duplicate_special_transformer_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="Special Transformer 1",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer1 = SpecialTransformerLV(
            general1,
            [BranchPresentation(sheet=self.sheet_guid)],
            SpecialTransformerLV.SpecialTransformerType(short_name="Type1"),
        )

        general2 = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="Special Transformer 2",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer2 = SpecialTransformerLV(
            general2,
            [BranchPresentation(sheet=self.sheet_guid)],
            SpecialTransformerLV.SpecialTransformerType(short_name="Type2"),
        )

        # Register first special transformer
        special_transformer1.register(self.network)
        self.assertEqual(
            self.network.special_transformers[
                self.special_transformer_guid
            ].general.name,
            "Special Transformer 1",
        )

        # Register second special transformer with same GUID should overwrite
        special_transformer2.register(self.network)
        # Verify special transformer was overwritten
        self.assertEqual(
            self.network.special_transformers[
                self.special_transformer_guid
            ].general.name,
            "Special Transformer 2",
        )

    def test_minimal_special_transformer_serialization(self) -> None:
        """Test that minimal special transformers serialize correctly with only required fields."""
        general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="MinimalSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            short_name="MinimalType"
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer = SpecialTransformerLV(
            general, [presentation], special_transformer_type
        )
        special_transformer.register(self.network)

        serialized = special_transformer.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#SpecialTransformerType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalSpecialTransformer'", serialized)
        self.assertIn("TapPosition:0", serialized)
        # CreationTime:0 is skipped when default

        # Should not have optional sections
        self.assertNotIn("#VoltageControl", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

        # Default boolean values (all True) are skipped when skip=True
        # Only non-default values will appear in serialized output

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that special transformers with multiple presentations serialize correctly."""
        general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="MultiPresSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            short_name="MultiType"
        )

        pres1 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$FF0000"))
        pres2 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$00FF00"))

        special_transformer = SpecialTransformerLV(
            general, [pres1, pres2], special_transformer_type
        )
        special_transformer.register(self.network)

        serialized = special_transformer.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_special_transformer_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="Test Special Transformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        result = general.serialize()

        # Should include required fields
        self.assertIn(
            f"GUID:'{{{str(self.special_transformer_guid).upper()}}}'", result
        )
        self.assertIn("Name:'Test Special Transformer'", result)
        self.assertIn("TapPosition:0", result)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", result)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", result)
        # CreationTime:0 is skipped when default

        # Should skip default values
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("FailureFrequency:", result)
        self.assertNotIn("Re:", result)

    def test_special_transformer_type_serialize_with_defaults(self) -> None:
        """Test SpecialTransformerType class serialization with default values."""
        special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            short_name="Test Type"
        )

        result = special_transformer_type.serialize()

        # Should include required fields
        self.assertIn("ShortName:'Test Type'", result)
        self.assertIn("Snom:0", result)
        self.assertIn("Ik2s:0", result)
        self.assertIn("TapSize:0", result)

        # Should skip default values
        self.assertNotIn("Sort:", result)  # Default 4 should be skipped

    def test_voltage_control_serialize_with_defaults(self) -> None:
        """Test VoltageControl class serialization with default values."""
        voltage_control = SpecialTransformerLV.VoltageControl()

        result = voltage_control.serialize()

        # CompoundingAtGeneration defaults to True and is not skipped
        self.assertEqual(
            result, "CompoundingAtGeneration:True"
        )  # Default VoltageControl shows non-skipped values

    def test_special_transformer_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = SpecialTransformerLV.General(
            guid=self.special_transformer_guid,
            name="Round Trip Special Transformer",
            creation_time=1234567890.0,
            node1=self.node1_guid,
            node2=self.node2_guid,
            switch_state1_L1=False,
            switch_state2_PE=True,
            type="TestType",
            tap_position=1.5,
        )

        original_special_transformer_type = SpecialTransformerLV.SpecialTransformerType(
            short_name="TestType",
            snom=1000.0,
            unom1=10.0,
            unom2=0.4,
            uknom=6.5,
            ik2s=10.0,
        )

        original_voltage_control = SpecialTransformerLV.VoltageControl(
            present=True,
            status=1,
            setpoint=0.38,
        )

        original_special_transformer = SpecialTransformerLV(
            general=original_general,
            presentations=[BranchPresentation(sheet=self.sheet_guid)],
            type=original_special_transformer_type,
            voltage_control=original_voltage_control,
        )

        original_special_transformer.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.special_transformer_guid),
                    "Name": "Round Trip Special Transformer",
                    "CreationTime": 1234567890.0,
                    "Node1": str(self.node1_guid),
                    "Node2": str(self.node2_guid),
                    "SwitchState1_L1": False,
                    "SwitchState2_PE": True,
                    "SpecialTransformerType": "TestType",
                    "TapPosition": 1.5,
                }
            ],
            "specialTransformerType": [
                {
                    "ShortName": "TestType",
                    "Snom": 1000.0,
                    "Unom1": 10.0,
                    "Unom2": 0.4,
                    "Uknom": 6.5,
                    "Ik2s": 10.0,
                }
            ],
            "voltageControl": [
                {
                    "Present": True,
                    "Status": 1,
                    "Setpoint": 0.38,
                }
            ],
            "presentations": [{"Sheet": str(self.sheet_guid)}],
        }

        deserialized = SpecialTransformerLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(
            deserialized.general.guid, original_special_transformer.general.guid
        )
        self.assertEqual(
            deserialized.general.name, original_special_transformer.general.name
        )
        self.assertEqual(
            deserialized.general.creation_time,
            original_special_transformer.general.creation_time,
        )
        self.assertEqual(
            deserialized.general.node1, original_special_transformer.general.node1
        )
        self.assertEqual(
            deserialized.general.node2, original_special_transformer.general.node2
        )
        self.assertEqual(
            deserialized.general.switch_state1_L1,
            original_special_transformer.general.switch_state1_L1,
        )
        self.assertEqual(
            deserialized.general.switch_state2_PE,
            original_special_transformer.general.switch_state2_PE,
        )
        self.assertEqual(
            deserialized.general.type, original_special_transformer.general.type
        )
        self.assertEqual(
            deserialized.general.tap_position,
            original_special_transformer.general.tap_position,
        )

        # Verify special transformer type properties
        self.assertEqual(
            deserialized.type.short_name, original_special_transformer.type.short_name
        )
        self.assertEqual(deserialized.type.snom, original_special_transformer.type.snom)
        self.assertEqual(
            deserialized.type.unom1, original_special_transformer.type.unom1
        )
        self.assertEqual(
            deserialized.type.unom2, original_special_transformer.type.unom2
        )
        self.assertEqual(
            deserialized.type.uknom, original_special_transformer.type.uknom
        )
        self.assertEqual(deserialized.type.ik2s, original_special_transformer.type.ik2s)

        # Verify voltage control properties
        self.assertIsNotNone(deserialized.voltage_control)
        self.assertIsNotNone(original_special_transformer.voltage_control)
        if (
            deserialized.voltage_control
            and original_special_transformer.voltage_control
        ):
            self.assertEqual(
                deserialized.voltage_control.present,
                original_special_transformer.voltage_control.present,
            )
            self.assertEqual(
                deserialized.voltage_control.status,
                original_special_transformer.voltage_control.status,
            )
            self.assertEqual(
                deserialized.voltage_control.setpoint,
                original_special_transformer.voltage_control.setpoint,
            )

        # Verify presentations
        self.assertEqual(
            len(deserialized.presentations),
            len(original_special_transformer.presentations),
        )
        if (
            len(deserialized.presentations) > 0
            and len(original_special_transformer.presentations) > 0
        ):
            self.assertEqual(
                deserialized.presentations[0].sheet,
                original_special_transformer.presentations[0].sheet,
            )


if __name__ == "__main__":
    unittest.main()
