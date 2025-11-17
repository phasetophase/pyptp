"""Tests for TSelectionLS GNF import/export functionality."""

import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import NodePresentation
from pyptp.elements.lv.selection import SelectionLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.IO.exporters.gnf_exporter import GnfExporter
from pyptp.IO.importers.gnf_importer import GnfImporter
from pyptp.network_lv import NetworkLV


class TestSelectionGnfIntegration(unittest.TestCase):
    """Test selection GNF import/export integration."""

    def setUp(self) -> None:
        """Create a network with selections for testing."""
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

        # Create and register some nodes for selection
        self.node1_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        node1 = NodeLV(
            NodeLV.General(guid=self.node1_guid, name="TestNode1"),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)

        self.node2_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))
        node2 = NodeLV(
            NodeLV.General(guid=self.node2_guid, name="TestNode2"),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)

        self.node3_guid = Guid(UUID("bec2228f-a78e-4f54-9ed2-0a7dbd48b3f7"))
        node3 = NodeLV(
            NodeLV.General(guid=self.node3_guid, name="TestNode3"),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node3.register(self.network)

        # Create selections
        selection1 = SelectionLV(
            SelectionLV.General(name="Knexis"),
            [
                SelectionLV.Object(guid=self.node1_guid),
                SelectionLV.Object(guid=self.node2_guid),
            ],
        )
        selection1.register(self.network)

        selection2 = SelectionLV(
            SelectionLV.General(name="Zon"), [SelectionLV.Object(guid=self.node3_guid)]
        )
        selection2.register(self.network)

        empty_selection = SelectionLV(SelectionLV.General(name="Empty"), [])
        empty_selection.register(self.network)

    def test_gnf_export_includes_selections(self) -> None:
        """Test that GNF export includes selection data."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            GnfExporter.export(self.network, tmp_path)

            with Path(tmp_path).open("r", encoding="utf-8-sig") as f:
                content = f.read()

            # Verify selection section exists
            self.assertIn("[SELECTION]", content)
            self.assertIn("Name:'Knexis'", content)
            self.assertIn("Name:'Zon'", content)
            self.assertIn("Name:'Empty'", content)

            # Verify object references
            self.assertIn(f"#Object GUID:'{{{str(self.node1_guid).upper()}}}'", content)
            self.assertIn(f"#Object GUID:'{{{str(self.node2_guid).upper()}}}'", content)
            self.assertIn(f"#Object GUID:'{{{str(self.node3_guid).upper()}}}'", content)

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_gnf_import_export_round_trip(self) -> None:
        """Test that selections survive a GNF export/import round trip."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Export original network
            GnfExporter.export(self.network, tmp_path)

            # Import it back
            importer = GnfImporter()
            imported_network = importer.import_gnf(tmp_path)

            # Verify selections were imported correctly
            self.assertEqual(len(imported_network.selections), 3)

            # Helper function to find selection by name
            def find_selection_by_name(name: str) -> SelectionLV | None:
                for selection in imported_network.selections:
                    if selection.general.name == name:
                        return selection
                return None

            # Verify "Knexis" selection
            knexis_selection = find_selection_by_name("Knexis")
            assert knexis_selection is not None
            self.assertEqual(knexis_selection.general.name, "Knexis")
            self.assertEqual(len(knexis_selection.objects), 2)
            knexis_guids = [obj.guid for obj in knexis_selection.objects]
            self.assertIn(self.node1_guid, knexis_guids)
            self.assertIn(self.node2_guid, knexis_guids)

            # Verify "Zon" selection
            zon_selection = find_selection_by_name("Zon")
            assert zon_selection is not None
            self.assertEqual(zon_selection.general.name, "Zon")
            self.assertEqual(len(zon_selection.objects), 1)
            zon_guids = [obj.guid for obj in zon_selection.objects]
            self.assertIn(self.node3_guid, zon_guids)

            # Verify "Empty" selection
            empty_selection = find_selection_by_name("Empty")
            assert empty_selection is not None
            self.assertEqual(empty_selection.general.name, "Empty")
            self.assertEqual(len(empty_selection.objects), 0)

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_gnf_export_with_no_selections(self) -> None:
        """Test that GNF export works correctly when there are no selections."""
        # Create a network without selections
        network_without_selections = NetworkLV()

        # Create and register a sheet
        sheet = SheetLV(
            SheetLV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(network_without_selections)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            GnfExporter.export(network_without_selections, tmp_path)

            with Path(tmp_path).open("r", encoding="utf-8-sig") as f:
                content = f.read()

            # Selection section should not be present when there are no selections
            self.assertNotIn("[SELECTION]", content)

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_selection_serialization_format_matches_pascal(self) -> None:
        """Test that selection serialization format matches the Pascal implementation."""
        selection = SelectionLV(
            SelectionLV.General(name="Knexis"),
            [
                SelectionLV.Object(guid=self.node1_guid),
                SelectionLV.Object(guid=self.node2_guid),
            ],
        )

        serialized = selection.serialize()

        # Check format matches Pascal: #General Name:'...' followed by #Object GUID:'...'
        lines = serialized.split("\n")
        self.assertTrue(lines[0].startswith("#General"))
        self.assertIn("Name:'Knexis'", lines[0])

        # Check object lines
        object_lines = [line for line in lines if line.startswith("#Object")]
        self.assertEqual(len(object_lines), 2)
        self.assertTrue(all("GUID:" in line for line in object_lines))


if __name__ == "__main__":
    unittest.main()
