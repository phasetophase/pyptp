"""Tests for GeneratorMV registration and serialization."""

import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.generator import GeneratorMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestGeneratorMV(unittest.TestCase):
    """Test MV generator registration and serialization."""

    def setUp(self) -> None:
        self.network = NetworkMV()

        sheet = SheetMV(
            SheetMV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")),
                name="TestNode",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.generator_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def _make_generator(self, **general_kwargs) -> GeneratorMV:
        general_kwargs.setdefault("guid", self.generator_guid)
        general_kwargs.setdefault("node", self.node_guid)
        general_kwargs.setdefault("name", "TestGenerator")
        general = GeneratorMV.General(**general_kwargs)
        presentation = ElementPresentation(sheet=self.sheet_guid)
        return GeneratorMV(general, [presentation])

    def test_registration(self) -> None:
        generator = self._make_generator()
        generator.register(self.network)

        self.assertIn(self.generator_guid, self.network.generators)
        self.assertIs(self.network.generators[self.generator_guid], generator)

    def test_duplicate_registration_overwrites(self) -> None:
        self._make_generator(name="First").register(self.network)
        self._make_generator(name="Second").register(self.network)

        self.assertEqual(len(self.network.generators), 1)
        self.assertEqual(
            self.network.generators[self.generator_guid].general.name, "Second"
        )

    def test_minimal_serialization(self) -> None:
        generator = self._make_generator()
        generator.register(self.network)
        serialized = generator.serialize()

        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)
        self.assertIn("Name:'TestGenerator'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("Sort:'G'", serialized)
        self.assertNotIn("#Restriction", serialized)

    def test_full_properties_serialization(self) -> None:
        generator = self._make_generator(
            creation_time=123.45,
            variant=True,
            switch_state=False,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            sort="G",
            snom=500.0,
            P=100.0,
            Q=50.0,
            ik_inom=1.2,
        )
        generator.register(self.network)
        serialized = generator.serialize()

        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:0", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4", serialized)
        self.assertIn("MaintenanceCancelDuration:1", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("Snom:500", serialized)
        self.assertIn("P:100", serialized)
        self.assertIn("Q:50", serialized)
        self.assertIn("Ik/Inom:1.2", serialized)

    def test_profile_serialization(self) -> None:
        generator = self._make_generator()
        generator.register(self.network)
        generator.serialize()

        # Default profile should not be written (skip=NIL_GUID behavior)
        # A custom profile should appear
        custom_profile = Guid(UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"))
        generator2 = self._make_generator(
            guid=Guid(UUID("11111111-2222-3333-4444-555555555555")),
            profile=custom_profile,
        )
        generator2.register(self.network)
        serialized2 = generator2.serialize()
        self.assertIn(f"Profile:'{{{str(custom_profile).upper()}}}'", serialized2)

    def test_with_restrictions(self) -> None:
        generator = self._make_generator()
        generator.restrictions.append(
            GeneratorMV.CapacityRestriction(
                sort="TestSort",
                begin_date=20230101,
                end_date=20231231,
                begin_time=8.0,
                end_time=18.0,
                p_max=80.0,
            )
        )
        generator.register(self.network)
        serialized = generator.serialize()

        self.assertIn("#Restriction", serialized)
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("Pmax:80", serialized)

    def test_extras_and_notes(self) -> None:
        generator = self._make_generator()
        generator.extras.append(Extra(text="foo=bar"))
        generator.notes.append(Note(text="Test note"))
        generator.register(self.network)
        serialized = generator.serialize()

        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_section_order(self) -> None:
        generator = self._make_generator()
        generator.restrictions.append(GeneratorMV.CapacityRestriction(sort="A"))
        generator.extras.append(Extra(text="x=1"))
        generator.notes.append(Note(text="note"))
        generator.register(self.network)
        serialized = generator.serialize()
        lines = serialized.split("\n")

        general_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#General")
        )
        restriction_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#Restriction")
        )
        extra_pos = next(i for i, line in enumerate(lines) if line.startswith("#Extra"))
        note_pos = next(i for i, line in enumerate(lines) if line.startswith("#Note"))
        presentation_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#Presentation")
        )

        self.assertLess(general_pos, restriction_pos)
        self.assertLess(restriction_pos, extra_pos)
        self.assertLess(extra_pos, note_pos)
        self.assertLess(note_pos, presentation_pos)

    def test_multiple_notes_serialize_to_single_line(self) -> None:
        """Multiple notes collapse into one chr(20)-joined #Note Text: line."""
        generator = self._make_generator()
        generator.notes.append(Note(text="a"))
        generator.notes.append(Note(text="b"))
        generator.register(self.network)
        serialized = generator.serialize()

        self.assertEqual(serialized.count("#Note"), 1)
        self.assertIn("#Note Text:a\x14b", serialized)

    def test_multiple_notes_round_trip(self) -> None:
        """Two notes survive a save/load round trip as two list entries."""
        generator = self._make_generator()
        generator.notes.append(Note(text="a"))
        generator.notes.append(Note(text="b"))
        generator.register(self.network)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.vnf"
            self.network.save(str(path))
            reloaded = NetworkMV.from_file(str(path))

        loaded = reloaded.generators[self.generator_guid]
        self.assertEqual([note.text for note in loaded.notes], ["a", "b"])

    def test_note_with_embedded_newline_round_trip(self) -> None:
        """A note with an embedded newline reloads as two notes (Vision-identical).

        Vision stores one note as a single string and has no list to preserve, so a
        newline inside a note reloads as two lines / two list entries.
        """
        generator = self._make_generator()
        generator.notes.append(Note(text="line1\nline2"))
        generator.register(self.network)
        serialized = generator.serialize()
        self.assertIn("#Note Text:line1\x14line2", serialized)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.vnf"
            self.network.save(str(path))
            reloaded = NetworkMV.from_file(str(path))

        loaded = reloaded.generators[self.generator_guid]
        self.assertEqual([note.text for note in loaded.notes], ["line1", "line2"])


if __name__ == "__main__":
    unittest.main()
