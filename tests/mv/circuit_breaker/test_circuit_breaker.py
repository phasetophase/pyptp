"""Tests for TCircuitBreakerMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.circuit_breaker import CircuitBreakerMV
from pyptp.elements.mv.presentations import SecondaryPresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestCircuitBreakerRegistration(unittest.TestCase):
    """Test circuit breaker registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet for testing."""
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

        self.breaker_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("12345678-9abc-def0-1234-56789abcdef0"))

    def test_circuit_breaker_registration_works(self) -> None:
        """Test that circuit breakers can register themselves with the network."""
        general = CircuitBreakerMV.General(guid=self.breaker_guid, name="TestBreaker")
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        # Verify breaker is in network
        self.assertIn(self.breaker_guid, self.network.circuit_breakers)
        self.assertIs(self.network.circuit_breakers[self.breaker_guid], breaker)

    def test_circuit_breaker_with_full_properties_serializes_correctly(self) -> None:
        """Test that circuit breakers with all properties serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullBreaker",
            in_object=self.in_object_guid,
            side=2,
            is_loadswitch=True,
            spontaneous_frequency=0.01,
            remote_status_indication=True,
            remote_controlled=True,
            refusal_chance=0.05,
            failure_frequency=0.02,
            repair_duration=2.5,
            ignore_for_selectivity=True,
            type="TestType",
            current_protection1_present=True,
            current_protection1_active=True,
            current_protection1_info="CP1 Info",
            current_protection1_direction=2,
            current_protection1_rca=1.5,
            current_protection1_type="CP1 Type",
            current_protection2_present=True,
            current_protection2_active=True,
            current_protection2_info="CP2 Info",
            current_protection2_direction=3,
            current_protection2_rca=2.0,
            current_protection2_type="CP2 Type",
            earth_fault_protection1_present=True,
            earth_fault_protection1_active=True,
            earth_fault_protection1_info="EFP1 Info",
            earth_fault_protection1_direction=1,
            earth_fault_protection1_rca=0.5,
            earth_fault_protection1_type="EFP1 Type",
            earth_fault_protection2_present=True,
            earth_fault_protection2_active=True,
            earth_fault_protection2_info="EFP2 Info",
            earth_fault_protection2_direction=2,
            earth_fault_protection2_rca=0.7,
            earth_fault_protection2_type="EFP2 Type",
            voltage_protection_present=True,
            voltage_protection_active=True,
            voltage_protection_info="VP Info",
            voltage_protection_direction=1,
            voltage_protection_rca=1.2,
            voltage_protection_type="VP Type",
            differential_protection_present=True,
            differential_protection_active=True,
            differential_protection_info="DP Info",
            distance_protection_present=True,
            distance_protection_active=True,
            distance_protection_info="DstP Info",
            distance_protection_type="DstP Type",
            voltage_protection2_present=True,
            voltage_protection2_active=True,
            voltage_protection2_info="VP2 Info",
            voltage_protection2_direction=3,
            voltage_protection2_rca=1.8,
            voltage_protection2_type="VP2 Type",
            differential_protection2_present=True,
            differential_protection2_active=True,
            differential_protection2_info="DP2 Info",
            unbalance_protection_present=True,
            unbalance_protection_active=True,
            unbalance_protection_info="UP Info",
            unbalance_protection_type="UP Type",
            thermal_protection_present=True,
            thermal_protection_active=True,
            thermal_protection_info="TP Info",
            earth_fault_differential_protection_present=True,
            earth_fault_differential_protection_active=True,
            earth_fault_differential_protection_info="EFDP Info",
            vector_shift_protection_present=True,
            vector_shift_protection_active=True,
            vector_shift_protection_info="VJP Info",
            frequency_protection_present=True,
            frequency_protection_active=True,
            frequency_protection_info="FP Info",
            transfer_trip_ability=True,
            transfer_trip_runtime=5.0,
            block_ability=True,
            reserve_ability=True,
            reserve_extra_time=3.0,
        )

        breaker_type = CircuitBreakerMV.CircuitBreakerType(
            short_name="TestBreakerType",
            unom=20.0,
            inom=630.0,
            switch_time=0.05,
            ik_make=25.0,
            ik_break=20.0,
            ik_dynamic=63.0,
            ik_thermal=25.0,
            t_thermal=1.0,
        )

        current_protection1_type = CircuitBreakerMV.ProtectionType(
            short_name="TestCP1Type",
            inom=400.0,
            t_input=0.1,
            t_output=0.2,
            setting_sort=1,
            I_great=1.2,
            T_great=0.5,
            I_greater=2.0,
            T_greater=0.1,
            drop_off_pickup_ratio=0.95,
        )

        thermal_protection = CircuitBreakerMV.ThermalProtection(
            i_pre=1.0,
            fa=1.05,
            Q=0.95,
            I_great=1.2,
            tau_great=10.0,
            I_start=6.0,
            tau_start=60.0,
            I_greater=1.5,
            T_greater=1.0,
            drop_off_pickup_ratio=0.95,
        )

        voltage_protection = CircuitBreakerMV.VoltageProtectionType(
            short_name="TestVoltageProtection",
            unom=20.0,
            t_input=0.1,
            t_output=0.2,
            u_small=18.0,
            t_small=1.0,
            u_smaller=16.0,
            t_smaller=0.5,
            u_great=22.0,
            t_great=2.0,
            u_greater=24.0,
            t_greater=0.1,
            ue_great=21.0,
            te_great=1.5,
        )

        distance_protection = CircuitBreakerMV.DistanceProtectionType(
            short_name="TestDistanceProtection",
            t_input=0.1,
            t_output=0.2,
            ie_great=0.1,
            i_great=0.5,
            u_small=18.0,
            z_small=5.0,
            kn=0.5,
            kn_angle=60.0,
        )

        differential_protection_type = CircuitBreakerMV.DifferentialProtectionType(
            name="TestDifferentialProtection",
            t_input=0.1,
            t_output=0.2,
            setting_sort=1,
            dI_great=0.3,
            t_great=0.5,
            dI_greater=0.8,
            t_greater=0.1,
            m=0.3,
            d_Id=0.2,
            release_by_current_protection=True,
            no_own_measurement=True,
        )

        earth_fault_differential_protection = (
            CircuitBreakerMV.EarthFaultDifferentialProtection(
                dI_great=0.1,
                t_great=0.5,
                other_measure_point=self.in_object_guid,
            )
        )

        vector_shift_protection = CircuitBreakerMV.VectorShiftProtection(
            d_phi_great=30.0,
            t_great=0.5,
        )

        frequency_protection = CircuitBreakerMV.FrequencyProtection(
            Fsmall=49.0,
            Fgreat=51.0,
        )

        presentation = SecondaryPresentation(
            sheet=self.sheet_guid,
            distance=100,
            otherside=True,
            color=DelphiColor("$FF0000"),
            size=2,
            width=3,
            text_color=DelphiColor("$00FF00"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=10,
            strings_y=20,
            note_x=50,
            note_y=60,
        )

        breaker = CircuitBreakerMV(
            general=general,
            type=breaker_type,
            current_protection1_type=current_protection1_type,
            thermal_protection=thermal_protection,
            voltage_protection=voltage_protection,
            distance_protection=distance_protection,
            differential_protection_type=differential_protection_type,
            earth_fault_differential_protection=earth_fault_differential_protection,
            vector_shift_protection=vector_shift_protection,
            frequency_protection=frequency_protection,
            presentations=[presentation],
            # differential_measure_points=[],  # Would need proper Guid list
            # block_protections=[],  # Would need proper list[tuple[int, Guid, int]]
            # reserve_switches=[],  # Would need proper Guid list
            # transfer_trip_switches=[],  # Would need proper list[tuple[int, Guid]]
        )
        breaker.extras.append(Extra(text="foo=bar"))
        breaker.notes.append(Note(text="Test note"))
        breaker.register(self.network)

        # Test serialization
        serialized = breaker.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#CircuitBreakerType"), 1)
        self.assertEqual(serialized.count("#CurrentProtection1Type"), 1)
        self.assertEqual(serialized.count("#ThermalProtection"), 1)
        self.assertEqual(serialized.count("#VoltageProtectionType"), 1)
        self.assertEqual(serialized.count("#DistanceProtectionType"), 1)
        self.assertEqual(serialized.count("#DifferentialProtectionType"), 1)
        self.assertEqual(serialized.count("#EarthFaultDifferentialProtection"), 1)
        self.assertEqual(serialized.count("#VectorJumpProtection"), 1)
        self.assertEqual(serialized.count("#FrequencyProtection"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullBreaker'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("Side:2", serialized)
        self.assertIn("IsLoadSwitch:True", serialized)
        self.assertIn("SpontaneousFrequency:0.01", serialized)
        self.assertIn("RemoteStatusIndication:True", serialized)
        self.assertIn("RemoteControl:True", serialized)
        self.assertIn("RefusalChance:0.05", serialized)
        self.assertIn("FailureFrequency:0.02", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("IgnoreForSelectivity:True", serialized)
        self.assertIn("CircuitBreakerType:'TestType'", serialized)
        self.assertIn("CurrentProtection1Present:True", serialized)
        self.assertIn("CurrentProtection1Active:True", serialized)
        self.assertIn("CurrentProtection1Info:'CP1 Info'", serialized)
        self.assertIn("CurrentProtection1Direction:2", serialized)
        self.assertIn("CurrentProtection1RCA:1.5", serialized)
        self.assertIn("CurrentProtection1Type:'CP1 Type'", serialized)
        self.assertIn("TransferTripAbility:True", serialized)
        self.assertIn("TransferTripRuntime:5.0", serialized)
        self.assertIn("BlockAbility:True", serialized)
        self.assertIn("ReserveAbility:True", serialized)
        self.assertIn("ReserveExtraTime:3", serialized)

        # Verify InObject reference
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)

        # Verify breaker type properties
        self.assertIn("ShortName:'TestBreakerType'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Inom:630", serialized)
        self.assertIn("SwitchTime:0.05", serialized)
        self.assertIn("IkMake:25", serialized)
        self.assertIn("IkBreak:20", serialized)
        self.assertIn("IkDynamic:63", serialized)
        self.assertIn("IkThermal:25", serialized)
        self.assertIn("Tthermal:1", serialized)

        # Verify protection type sections are included
        self.assertIn("#CurrentProtection1Type ShortName:'TestCP1Type'", serialized)
        self.assertIn("Inom:400", serialized)
        self.assertIn("SettingSort:1", serialized)
        self.assertIn("I>:1.2", serialized)

        # Verify thermal protection properties
        self.assertIn("Ipre:1", serialized)
        self.assertIn("Fa:1.05", serialized)
        self.assertIn("Q:0.95", serialized)
        self.assertIn("I>:1.2", serialized)
        self.assertIn("Tau>:10", serialized)
        self.assertIn("IStart:6", serialized)
        self.assertIn("TauStart:60", serialized)
        self.assertIn("I>>:1.5", serialized)
        self.assertIn("T>>:1", serialized)
        self.assertIn("DropOffPickupRatio:0.95", serialized)

        # Verify voltage protection properties
        self.assertIn("ShortName:'TestVoltageProtection'", serialized)
        self.assertIn("U<:18", serialized)
        self.assertIn("T<:1", serialized)
        self.assertIn("U<<:16", serialized)
        self.assertIn("T<<:0.5", serialized)
        self.assertIn("U>:22", serialized)
        self.assertIn("T>:2", serialized)
        self.assertIn("U>>:24", serialized)
        self.assertIn("T>>:0.1", serialized)
        self.assertIn("Ue>:21", serialized)
        self.assertIn("Te>:1.5", serialized)

        # Verify distance protection properties
        self.assertIn("ShortName:'TestDistanceProtection'", serialized)
        self.assertIn("Ie>:0.1", serialized)
        self.assertIn("I>:0.5", serialized)
        self.assertIn("U<:18", serialized)
        self.assertIn("Z<:5", serialized)
        self.assertIn("Kn:0.5", serialized)
        self.assertIn("KnAngle:60", serialized)

        # Verify differential protection properties
        self.assertIn("Name:'TestDifferentialProtection'", serialized)
        self.assertIn("dI>:0.3", serialized)
        self.assertIn("T>:0.5", serialized)
        self.assertIn("dI>>:0.8", serialized)
        self.assertIn("T>>:0.1", serialized)
        self.assertIn("m:0.3", serialized)
        self.assertIn("dId:0.2", serialized)
        self.assertIn("ReleaseByCurrentProtection:True", serialized)
        self.assertIn("NoOwnMeasurement:True", serialized)

        # Verify earth fault differential protection properties
        self.assertIn("dI>:0.1", serialized)
        self.assertIn("T>:0.5", serialized)
        self.assertIn(
            f"OtherMeasurePoint:'{{{str(self.in_object_guid).upper()}}}'", serialized
        )

        # Verify vector jump protection properties
        self.assertIn("Phi>:30", serialized)
        self.assertIn("#VectorJumpProtection", serialized)

        # Verify frequency protection properties
        self.assertIn("F<:49", serialized)
        self.assertIn("F>:51", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Distance:100", serialized)
        self.assertIn("Otherside:True", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("StringsX:10", serialized)
        self.assertIn("StringsY:20", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a breaker with the same GUID overwrites the existing one."""
        general1 = CircuitBreakerMV.General(guid=self.breaker_guid, name="FirstBreaker")
        breaker1 = CircuitBreakerMV(
            general1, presentations=[SecondaryPresentation(sheet=self.sheet_guid)]
        )
        breaker1.register(self.network)

        general2 = CircuitBreakerMV.General(
            guid=self.breaker_guid, name="SecondBreaker"
        )
        breaker2 = CircuitBreakerMV(
            general2, presentations=[SecondaryPresentation(sheet=self.sheet_guid)]
        )
        breaker2.register(self.network)

        # Should only have one breaker
        self.assertEqual(len(self.network.circuit_breakers), 1)
        # Should be the second breaker
        self.assertEqual(
            self.network.circuit_breakers[self.breaker_guid].general.name,
            "SecondBreaker",
        )

    def test_minimal_circuit_breaker_serialization(self) -> None:
        """Test that minimal circuit breakers serialize correctly with only required fields."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid, name="MinimalBreaker"
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalBreaker'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

        # Should not have optional sections
        self.assertNotIn("#CircuitBreakerType", serialized)
        self.assertNotIn("#CurrentProtection1Type", serialized)
        self.assertNotIn("#ThermalProtection", serialized)

    def test_circuit_breaker_with_in_object_serializes_correctly(self) -> None:
        """Test that circuit breakers with InObject serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="InObjectBreaker",
            in_object=self.in_object_guid,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)

    def test_circuit_breaker_with_load_switch_serializes_correctly(self) -> None:
        """Test that circuit breakers with load switch flag serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="LoadSwitchBreaker",
            is_loadswitch=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("IsLoadSwitch:True", serialized)

    def test_circuit_breaker_with_remote_control_serializes_correctly(self) -> None:
        """Test that circuit breakers with remote control serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="RemoteControlBreaker",
            remote_status_indication=True,
            remote_controlled=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("RemoteStatusIndication:True", serialized)
        self.assertIn("RemoteControl:True", serialized)

    def test_circuit_breaker_with_failure_properties_serializes_correctly(self) -> None:
        """Test that circuit breakers with failure properties serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="FailureBreaker",
            spontaneous_frequency=0.01,
            refusal_chance=0.05,
            failure_frequency=0.02,
            repair_duration=2.5,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("SpontaneousFrequency:0.01", serialized)
        self.assertIn("RefusalChance:0.05", serialized)
        self.assertIn("FailureFrequency:0.02", serialized)
        self.assertIn("RepairDuration:2.5", serialized)

    def test_circuit_breaker_with_selectivity_serializes_correctly(self) -> None:
        """Test that circuit breakers with selectivity settings serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="SelectivityBreaker",
            ignore_for_selectivity=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("IgnoreForSelectivity:True", serialized)

    def test_circuit_breaker_with_protection_abilities_serializes_correctly(
        self,
    ) -> None:
        """Test that circuit breakers with protection abilities serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="ProtectionAbilitiesBreaker",
            transfer_trip_ability=True,
            transfer_trip_runtime=5.0,
            block_ability=True,
            reserve_ability=True,
            reserve_extra_time=3.0,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("TransferTripAbility:True", serialized)
        self.assertIn("TransferTripRuntime:5.0", serialized)
        self.assertIn("BlockAbility:True", serialized)
        self.assertIn("ReserveAbility:True", serialized)
        self.assertIn("ReserveExtraTime:3", serialized)

    def test_circuit_breaker_with_side_serializes_correctly(self) -> None:
        """Test that circuit breakers with side setting serialize correctly."""
        general = CircuitBreakerMV.General(
            guid=self.breaker_guid,
            name="SideBreaker",
            side=2,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        breaker = CircuitBreakerMV(general, presentations=[presentation])
        breaker.register(self.network)

        serialized = breaker.serialize()
        self.assertIn("Side:2", serialized)


if __name__ == "__main__":
    unittest.main()
