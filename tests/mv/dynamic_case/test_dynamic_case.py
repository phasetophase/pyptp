"""Tests for TDynamicCaseMS behavior."""

import unittest

from pyptp.elements.mv.dynamic_case import DynamicCaseMV


class TestDynamicCaseRegistration(unittest.TestCase):
    """Test dynamic case functionality."""

    def test_dynamic_case_with_full_properties_serializes_correctly(self) -> None:
        """Test that dynamic cases with all properties serialize correctly."""
        general = DynamicCaseMV.General(
            name="TestDynamicCase",
            description="Test dynamic case description",
        )

        dynamic_event1 = DynamicCaseMV.DynamicEvent(
            start_time=1.0,
            action="TestAction1",
            vision_object="TestObject1",
            fault_sort="TestFault1",
            ref_sort="TestRef1",
            parameter1=10.0,
            parameter2=20.0,
            parameter3=30.0,
        )

        dynamic_event2 = DynamicCaseMV.DynamicEvent(
            start_time=2.0,
            action="TestAction2",
            vision_object="TestObject2",
            fault_sort="TestFault2",
            ref_sort="TestRef2",
            parameter1=40.0,
            parameter2=50.0,
            parameter3=60.0,
        )

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=[dynamic_event1, dynamic_event2],
        )

        # Test serialization
        serialized = dynamic_case.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#DynamicEvent"), 2)

        # Verify general properties
        self.assertIn("Name:'TestDynamicCase'", serialized)
        self.assertIn("Description:'Test dynamic case description'", serialized)

        # Verify dynamic event properties
        self.assertIn("StartTime:1", serialized)
        self.assertIn("Action:'TestAction1'", serialized)
        self.assertIn("VisionObject:'TestObject1'", serialized)
        self.assertIn("FaultSort:'TestFault1'", serialized)
        self.assertIn("RefSort:'TestRef1'", serialized)
        self.assertIn("Parameter1:10", serialized)
        self.assertIn("Parameter2:20", serialized)
        self.assertIn("Parameter3:30", serialized)

        self.assertIn("StartTime:2", serialized)
        self.assertIn("Action:'TestAction2'", serialized)
        self.assertIn("VisionObject:'TestObject2'", serialized)
        self.assertIn("FaultSort:'TestFault2'", serialized)
        self.assertIn("RefSort:'TestRef2'", serialized)
        self.assertIn("Parameter1:40", serialized)
        self.assertIn("Parameter2:50", serialized)
        self.assertIn("Parameter3:60", serialized)

    def test_minimal_dynamic_case_serialization(self) -> None:
        """Test that minimal dynamic cases serialize correctly with only required fields."""
        general = DynamicCaseMV.General()
        dynamic_case = DynamicCaseMV(general=general, dynamic_events=[])

        serialized = dynamic_case.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#DynamicEvent"), 0)

        # Empty strings are skipped by default in serialization
        self.assertIn("#General", serialized)
        self.assertNotIn("Name:", serialized)
        self.assertNotIn("Description:", serialized)

    def test_dynamic_case_with_single_event_serializes_correctly(self) -> None:
        """Test that dynamic cases with single event serialize correctly."""
        general = DynamicCaseMV.General(
            name="SingleEventCase",
            description="Single event test case",
        )

        dynamic_event = DynamicCaseMV.DynamicEvent(
            start_time=5.0,
            action="SingleAction",
            vision_object="SingleObject",
            fault_sort="SingleFault",
            ref_sort="SingleRef",
            parameter1=100.0,
            parameter2=200.0,
            parameter3=300.0,
        )

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=[dynamic_event],
        )

        serialized = dynamic_case.serialize()

        # Should have one event
        self.assertEqual(serialized.count("#DynamicEvent"), 1)

        # Verify properties
        self.assertIn("Name:'SingleEventCase'", serialized)
        self.assertIn("Description:'Single event test case'", serialized)
        self.assertIn("StartTime:5", serialized)
        self.assertIn("Action:'SingleAction'", serialized)
        self.assertIn("VisionObject:'SingleObject'", serialized)
        self.assertIn("FaultSort:'SingleFault'", serialized)
        self.assertIn("RefSort:'SingleRef'", serialized)
        self.assertIn("Parameter1:100", serialized)
        self.assertIn("Parameter2:200", serialized)
        self.assertIn("Parameter3:300", serialized)

    def test_dynamic_case_with_no_events_serializes_correctly(self) -> None:
        """Test that dynamic cases with no events serialize correctly."""
        general = DynamicCaseMV.General(
            name="NoEventCase",
            description="No event test case",
        )

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=[],
        )

        serialized = dynamic_case.serialize()

        # Should have no events
        self.assertEqual(serialized.count("#DynamicEvent"), 0)

        # Verify properties
        self.assertIn("Name:'NoEventCase'", serialized)
        self.assertIn("Description:'No event test case'", serialized)

    def test_dynamic_case_with_zero_start_time_serializes_correctly(self) -> None:
        """Test that dynamic cases with zero start time serialize correctly."""
        general = DynamicCaseMV.General(
            name="ZeroTimeCase",
            description="Zero time test case",
        )

        dynamic_event = DynamicCaseMV.DynamicEvent(
            start_time=0.0,
            action="ZeroAction",
            vision_object="ZeroObject",
            fault_sort="ZeroFault",
            ref_sort="ZeroRef",
            parameter1=0.0,
            parameter2=0.0,
            parameter3=0.0,
        )

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=[dynamic_event],
        )

        serialized = dynamic_case.serialize()

        # Zero values are skipped by default in serialization
        self.assertNotIn("StartTime:", serialized)
        self.assertNotIn("Parameter1:", serialized)
        self.assertNotIn("Parameter2:", serialized)
        self.assertNotIn("Parameter3:", serialized)

        # Non-zero string values should be present
        self.assertIn("Action:'ZeroAction'", serialized)
        self.assertIn("VisionObject:'ZeroObject'", serialized)
        self.assertIn("FaultSort:'ZeroFault'", serialized)
        self.assertIn("RefSort:'ZeroRef'", serialized)

    def test_dynamic_case_with_multiple_events_serializes_correctly(self) -> None:
        """Test that dynamic cases with multiple events serialize correctly."""
        general = DynamicCaseMV.General(
            name="MultiEventCase",
            description="Multiple event test case",
        )

        events = []
        for i in range(3):
            event = DynamicCaseMV.DynamicEvent(
                start_time=float(i + 1),
                action=f"Action{i}",
                vision_object=f"Object{i}",
                fault_sort=f"Fault{i}",
                ref_sort=f"Ref{i}",
                parameter1=float(i * 10),
                parameter2=float(i * 20),
                parameter3=float(i * 30),
            )
            events.append(event)

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=events,
        )

        serialized = dynamic_case.serialize()

        # Should have three events
        self.assertEqual(serialized.count("#DynamicEvent"), 3)

        # Verify all events are present
        for i in range(3):
            self.assertIn(f"StartTime:{i + 1}", serialized)
            self.assertIn(f"Action:'Action{i}'", serialized)
            self.assertIn(f"VisionObject:'Object{i}'", serialized)
            self.assertIn(f"FaultSort:'Fault{i}'", serialized)
            self.assertIn(f"RefSort:'Ref{i}'", serialized)
            if i > 0:  # Only non-zero values are serialized
                self.assertIn(f"Parameter1:{i * 10}", serialized)
                self.assertIn(f"Parameter2:{i * 20}", serialized)
                self.assertIn(f"Parameter3:{i * 30}", serialized)

    def test_dynamic_case_with_empty_strings_serializes_correctly(self) -> None:
        """Test that dynamic cases with empty strings serialize correctly."""
        general = DynamicCaseMV.General(
            name="",
            description="",
        )

        dynamic_event = DynamicCaseMV.DynamicEvent(
            start_time=1.0,
            action="",
            vision_object="",
            fault_sort="",
            ref_sort="",
            parameter1=0.0,
            parameter2=0.0,
            parameter3=0.0,
        )

        dynamic_case = DynamicCaseMV(
            general=general,
            dynamic_events=[dynamic_event],
        )

        serialized = dynamic_case.serialize()

        # Empty strings are skipped by default in serialization
        self.assertNotIn("Name:", serialized)
        self.assertNotIn("Description:", serialized)
        self.assertNotIn("Action:", serialized)
        self.assertNotIn("VisionObject:", serialized)
        self.assertNotIn("FaultSort:", serialized)
        self.assertNotIn("RefSort:", serialized)

        # Only StartTime should be present since it's non-zero
        self.assertIn("StartTime:1", serialized)


if __name__ == "__main__":
    unittest.main()
