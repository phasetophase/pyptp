"""Unit tests for GnfExporter and VnfExporter core functionality and file format differences."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

from pyptp.elements.element_utils import Guid, guid_to_string
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import NodePresentation as NodePresentationMS
from pyptp.elements.mv.sheet import SheetMV
from pyptp.IO.exporters.gnf_exporter import GnfExporter
from pyptp.IO.exporters.vnf_exporter import VnfExporter
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


class TestGnfExporter(unittest.TestCase):
    """Test GnfExporter public interface and file structure."""

    def setUp(self):
        """Set up a minimal LV network with a sheet and mock properties."""
        self.network = NetworkLV()
        self.sheet_guid = Guid(UUID("12345678-1234-5678-9ABC-123456789ABC"))
        self.node_guid = Guid(UUID("87654321-4321-8765-CBA9-987654321CBA"))
        sheet = SheetLV(SheetLV.General(guid=self.sheet_guid, name="TestSheet"))
        sheet.register(self.network)
        self.network.properties = Mock()
        self.network.properties.serialize.return_value = "MockProperties"

    def test_export_basic_structure(self):
        """Export a minimal network and verify required sections and header."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            GnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertTrue(content.startswith("G8.9\nNETWORK\n\n"))
            self.assertIn("[PROPERTIES]", content)
            self.assertIn("MockProperties", content)
            self.assertIn("[COMMENTS]", content)
            self.assertIn("[SHEET]", content)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_export_with_node_content(self):
        """Export a network with a node and verify node data is present."""
        node = NodeLV(
            NodeLV.General(guid=self.node_guid, name="TestNode"),
            [NodePresentation(sheet=self.sheet_guid, x=100, y=200)],
        )
        node.register(self.network)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            GnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("[NODE]", content)
            self.assertIn("TestNode", content)
            self.assertIn(guid_to_string(self.node_guid), content)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_export_empty_sections_not_written(self):
        """Export with only required sections and verify no unnecessary sections are written."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            GnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r", encoding="utf-8-sig") as f:
                content = f.read()
            section_count = content.count("[")
            self.assertGreaterEqual(section_count, 4)
            self.assertLessEqual(section_count, 10)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestVnfExporter(unittest.TestCase):
    """Test VnfExporter public interface and file structure."""

    def setUp(self):
        """Set up a minimal MV network with a sheet and mock properties."""
        self.network = NetworkMV()
        self.sheet_guid = Guid(UUID("12345678-1234-5678-9ABC-123456789ABC"))
        self.node_guid = Guid(UUID("87654321-4321-8765-CBA9-987654321CBA"))
        sheet = SheetMV(SheetMV.General(guid=self.sheet_guid, name="TestSheet"))
        sheet.register(self.network)
        self.network.properties = Mock()
        self.network.properties.serialize.return_value = "MockProperties"

    def test_export_basic_structure(self):
        """Export a minimal network and verify required sections and header."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            VnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r") as f:
                content = f.read()
            self.assertTrue(content.startswith("V9.9\nNETWORK\n\n"))
            self.assertIn("[PROPERTIES]", content)
            self.assertIn("MockProperties", content)
            self.assertIn("[SHEET]", content)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_export_with_node_content(self):
        """Export a network with a node and verify node data is present."""
        node = NodeMV(
            NodeMV.General(guid=self.node_guid, name="TestNode"),
            presentations=[NodePresentationMS(sheet=self.sheet_guid, x=100, y=200)],
        )
        node.register(self.network)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            VnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r") as f:
                content = f.read()
            self.assertIn("[NODE]", content)
            self.assertIn("TestNode", content)
            self.assertIn(guid_to_string(self.node_guid), content)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_export_empty_sections_not_written(self):
        """Export with only required sections and verify no unnecessary sections are written."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            VnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r") as f:
                content = f.read()
            # Only PROPERTIES and SHEET should be present for empty network
            self.assertIn("[PROPERTIES]", content)
            self.assertIn("[SHEET]", content)
            # Empty sections should not be written
            empty_sections = [
                "[NODE]",
                "[LINK]",
                "[CABLE]",
                "[TRANSFORMER]",
                "[SOURCE]",
            ]
            for section in empty_sections:
                self.assertNotIn(
                    section, content, f"Empty section {section} should not be written"
                )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_export_file_encoding(self):
        """Export and verify VNF file does not start with BOM."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        try:
            VnfExporter.export(self.network, tmp_path)
            with Path(tmp_path).open("r") as f:
                content = f.read()
            self.assertFalse(content.startswith("\ufeff"))
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestExporterComparison(unittest.TestCase):
    """Test differences between GNF and VNF exporter file formats and encodings."""

    def test_file_headers_different(self):
        """Verify GNF and VNF files have different headers."""
        gnf_network = NetworkLV()
        vnf_network = NetworkMV()
        gnf_network.properties = Mock()
        gnf_network.properties.serialize.return_value = "MockProperties"
        vnf_network.properties = Mock()
        vnf_network.properties.serialize.return_value = "MockProperties"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as gnf_file:
            gnf_path = gnf_file.name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as vnf_file:
            vnf_path = vnf_file.name
        try:
            GnfExporter.export(gnf_network, gnf_path)
            VnfExporter.export(vnf_network, vnf_path)
            with Path(gnf_path).open("r", encoding="utf-8-sig") as f:
                gnf_content = f.read()
            with Path(vnf_path).open("r") as f:
                vnf_content = f.read()
            self.assertTrue(gnf_content.startswith("G8.9\nNETWORK\n\n"))
            self.assertTrue(vnf_content.startswith("V9.9\nNETWORK\n\n"))
        finally:
            Path(gnf_path).unlink(missing_ok=True)
            Path(vnf_path).unlink(missing_ok=True)

    def test_encoding_differences(self):
        """Verify GNF uses UTF-8 BOM and VNF does not."""
        gnf_network = NetworkLV()
        vnf_network = NetworkMV()
        gnf_network.properties = Mock()
        gnf_network.properties.serialize.return_value = "MockProperties"
        vnf_network.properties = Mock()
        vnf_network.properties.serialize.return_value = "MockProperties"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as gnf_file:
            gnf_path = gnf_file.name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".vnf", delete=False
        ) as vnf_file:
            vnf_path = vnf_file.name
        try:
            GnfExporter.export(gnf_network, gnf_path)
            VnfExporter.export(vnf_network, vnf_path)
            with Path(gnf_path).open("rb") as f:
                gnf_bytes = f.read()
            with Path(vnf_path).open("rb") as f:
                vnf_bytes = f.read()
            self.assertTrue(gnf_bytes.startswith(b"\xef\xbb\xbf"))
            self.assertFalse(vnf_bytes.startswith(b"\xef\xbb\xbf"))
        finally:
            Path(gnf_path).unlink(missing_ok=True)
            Path(vnf_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
