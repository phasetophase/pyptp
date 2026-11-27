"""Tests for version migration via native GaiaMigrator/VisionMigrator libraries.

These tests verify that older GNF/VNF files can be migrated to the current
version via the bundled native libraries. They run on any platform (macOS
uses the .dylib).

To run on a Mac:
    uv run python -m unittest tests.test_macos_migration -v
"""

import unittest
from pathlib import Path

from pyptp import NetworkLV, NetworkMV
from pyptp.convert.version_migrator import migrate_and_read


INPUT_DIR = Path(__file__).parent / "input_files"


class TestGnfVersionMigration(unittest.TestCase):
    """Test GNF version migration via the native GaiaMigrator library."""

    def test_migrate_g87_to_g812(self) -> None:
        """Test that a G8.7 file can be migrated to G8.12."""
        gnf_file = INPUT_DIR / "SO_output_G87.gnf"
        if not gnf_file.exists():
            self.skipTest("SO_output_G87.gnf not found")

        content = migrate_and_read(gnf_file, version="G8.12", encoding="utf-8-sig")

        self.assertTrue(
            content.startswith("G8.12"), "Migrated content should start with G8.12"
        )

    def test_from_file_g87_with_migration(self) -> None:
        """Test that NetworkLV.from_file() handles a G8.7 file via automatic migration."""
        gnf_file = INPUT_DIR / "SO_output_G87.gnf"
        if not gnf_file.exists():
            self.skipTest("SO_output_G87.gnf not found")

        network = NetworkLV.from_file(str(gnf_file))

        self.assertIsInstance(network, NetworkLV)
        self.assertEqual(len(network.nodes), 70)
        self.assertEqual(len(network.cables), 68)

    def test_from_file_g87_existing(self) -> None:
        """Test that the existing AllComponents_v87 migrates correctly."""
        gnf_file = INPUT_DIR / "AllComponents_v87.gnf"
        if not gnf_file.exists():
            self.skipTest("AllComponents_v87.gnf not found")

        network = NetworkLV.from_file(str(gnf_file))

        self.assertIsInstance(network, NetworkLV)
        self.assertGreater(len(network.nodes), 0)


class TestVnfVersionMigration(unittest.TestCase):
    """Test VNF version migration via the native VisionMigrator library."""

    def test_migrate_v97_to_v912(self) -> None:
        """Test that a V9.7 file can be migrated to V9.12."""
        vnf_file = INPUT_DIR / "AllComponents_v97.vnf"
        if not vnf_file.exists():
            self.skipTest("AllComponents_v97.vnf not found")

        content = migrate_and_read(vnf_file, version="V9.12", encoding="utf-8-sig")

        self.assertTrue(
            content.startswith("V9.12"), "Migrated content should start with V9.12"
        )

    def test_from_file_v97_existing(self) -> None:
        """Test that the existing AllComponents_v97 migrates correctly."""
        vnf_file = INPUT_DIR / "AllComponents_v97.vnf"
        if not vnf_file.exists():
            self.skipTest("AllComponents_v97.vnf not found")

        network = NetworkMV.from_file(str(vnf_file))

        self.assertIsInstance(network, NetworkMV)
        self.assertGreater(len(network.nodes), 0)


if __name__ == "__main__":
    unittest.main()
