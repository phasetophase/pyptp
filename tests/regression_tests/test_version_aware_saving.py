"""Tests for version-aware saving functionality across GNF and VNF formats.

Validates that networks can be saved to different format versions while preserving
element counts and GUIDs through round-trip load → save → reload cycles.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from pyptp import GnfVersion, NetworkLV, NetworkMV, VnfVersion
from pyptp.elements.element_utils import Guid


class TestGnfVersionAwareSaving(unittest.TestCase):
    """Test version-aware saving for GNF (LV) networks."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents.gnf"
        self.output_dir = self.root / "output_files" / "version_aware_saving"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_header(self, path: Path) -> str:
        """Extract the version header (first line) from a file."""
        with path.open(encoding="utf-8-sig") as f:
            return f.readline().strip()

    def _get_element_counts(self, network: NetworkLV) -> dict[str, int]:
        """Get counts of all element types in the network."""
        return {
            "nodes": len(network.nodes),
            "cables": len(network.cables),
            "links": len(network.links),
            "transformers": len(network.transformers),
            "special_transformers": len(network.special_transformers),
            "sources": len(network.sources),
            "loads": len(network.loads),
            "fuses": len(network.fuses),
            "circuit_breakers": len(network.circuit_breakers),
            "sheets": len(network.sheets),
            "homes": len(network.homes),
            "batteries": len(network.batteries),
            "pvs": len(network.pvs),
        }

    def _get_all_guids(self, network: NetworkLV) -> dict[str, set[Guid]]:
        """Get all GUIDs for each element type in the network."""
        return {
            "nodes": set(network.nodes.keys()),
            "cables": set(network.cables.keys()),
            "links": set(network.links.keys()),
            "transformers": set(network.transformers.keys()),
            "special_transformers": set(network.special_transformers.keys()),
            "sources": set(network.sources.keys()),
            "loads": set(network.loads.keys()),
            "fuses": set(network.fuses.keys()),
            "circuit_breakers": set(network.circuit_breakers.keys()),
            "sheets": set(network.sheets.keys()),
            "homes": set(network.homes.keys()),
            "batteries": set(network.batteries.keys()),
            "pvs": set(network.pvs.keys()),
        }

    def test_gnf_version_roundtrip(self) -> None:
        """Test save/reload preserves header, element counts, and GUIDs for all GNF versions."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        network_original = NetworkLV.from_file(self.input_file)
        original_counts = self._get_element_counts(network_original)
        original_guids = self._get_all_guids(network_original)

        for version in GnfVersion:
            with self.subTest(version=version):
                output_file = self.output_dir / f"AllComponents_{version.name}.gnf"
                network_original.save(output_file, version)

                # Check header
                header = self._get_file_header(output_file)
                self.assertEqual(header, version.value, "Header mismatch")

                # Reload and check counts
                network_reloaded = NetworkLV.from_file(output_file)
                reloaded_counts = self._get_element_counts(network_reloaded)
                self.assertEqual(
                    original_counts, reloaded_counts, "Element counts differ"
                )

                # Check GUIDs
                reloaded_guids = self._get_all_guids(network_reloaded)
                for element_type in original_guids:
                    self.assertEqual(
                        original_guids[element_type],
                        reloaded_guids[element_type],
                        f"{element_type} GUIDs differ",
                    )


class TestVnfVersionAwareSaving(unittest.TestCase):
    """Test version-aware saving for VNF (MV) networks."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents.vnf"
        self.output_dir = self.root / "output_files" / "version_aware_saving"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_header(self, path: Path) -> str:
        """Extract the version header (first line) from a file."""
        with path.open(encoding="utf-8-sig") as f:
            return f.readline().strip()

    def _get_element_counts(self, network: NetworkMV) -> dict[str, int]:
        """Get counts of all element types in the network."""
        return {
            "nodes": len(network.nodes),
            "cables": len(network.cables),
            "links": len(network.links),
            "transformers": len(network.transformers),
            "special_transformers": len(network.special_transformers),
            "sources": len(network.sources),
            "loads": len(network.loads),
            "fuses": len(network.fuses),
            "circuit_breakers": len(network.circuit_breakers),
            "sheets": len(network.sheets),
            "batteries": len(network.batteries),
            "pvs": len(network.pvs),
        }

    def _get_all_guids(self, network: NetworkMV) -> dict[str, set[Guid]]:
        """Get all GUIDs for each element type in the network."""
        return {
            "nodes": set(network.nodes.keys()),
            "cables": set(network.cables.keys()),
            "links": set(network.links.keys()),
            "transformers": set(network.transformers.keys()),
            "special_transformers": set(network.special_transformers.keys()),
            "sources": set(network.sources.keys()),
            "loads": set(network.loads.keys()),
            "fuses": set(network.fuses.keys()),
            "circuit_breakers": set(network.circuit_breakers.keys()),
            "sheets": set(network.sheets.keys()),
            "batteries": set(network.batteries.keys()),
            "pvs": set(network.pvs.keys()),
        }

    def test_vnf_version_roundtrip(self) -> None:
        """Test save/reload preserves header, element counts, and GUIDs for all VNF versions."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        network_original = NetworkMV.from_file(self.input_file)
        original_counts = self._get_element_counts(network_original)
        original_guids = self._get_all_guids(network_original)

        for version in VnfVersion:
            with self.subTest(version=version):
                output_file = self.output_dir / f"AllComponents_{version.name}.vnf"
                network_original.save(output_file, version)

                # Check header
                header = self._get_file_header(output_file)
                self.assertEqual(header, version.value, "Header mismatch")

                # Reload and check counts
                network_reloaded = NetworkMV.from_file(output_file)
                reloaded_counts = self._get_element_counts(network_reloaded)
                self.assertEqual(
                    original_counts, reloaded_counts, "Element counts differ"
                )

                # Check GUIDs
                reloaded_guids = self._get_all_guids(network_reloaded)
                for element_type in original_guids:
                    self.assertEqual(
                        original_guids[element_type],
                        reloaded_guids[element_type],
                        f"{element_type} GUIDs differ",
                    )


if __name__ == "__main__":
    unittest.main()
