"""Tests for version migration via native GaiaMigrator/VisionMigrator libraries.

These tests verify that older GNF/VNF files can be migrated to the current
version via the bundled native libraries. They run on any platform (Windows
uses the .dll, Linux uses the .so).

To run on Linux from a Windows machine:
    docker build -f Dockerfile.test -t pyptp-linux-test .
    docker run --rm pyptp-linux-test
"""

import unittest
from pathlib import Path

from pyptp import NetworkLV
from pyptp.convert.version_migrator import migrate_and_read


INPUT_DIR = Path(__file__).parent / "input_files"


class TestGnfVersionMigration(unittest.TestCase):
    """Test GNF version migration via the native GaiaMigrator library."""

    def test_migrate_g87_to_g89(self) -> None:
        """Test that a G8.7 file can be migrated to G8.9."""
        gnf_file = INPUT_DIR / "SO_output_G87.gnf"
        if not gnf_file.exists():
            self.skipTest("SO_output_G87.gnf not found")

        content = migrate_and_read(gnf_file, version="G8.9", encoding="utf-8-sig")

        self.assertTrue(
            content.startswith("G8.9"), "Migrated content should start with G8.9"
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


if __name__ == "__main__":
    unittest.main()
