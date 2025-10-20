"""Tests for NetworkLV and NetworkMV I/O convenience methods."""

import unittest
from pathlib import Path

from pyptp import NetworkLV, NetworkMV


class TestNetworkLVIO(unittest.TestCase):
    """Test NetworkLV.from_file() and save() methods."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.test_root = Path(__file__).parent
        self.input_file = self.test_root / "input_files" / "AllComponents.gnf"
        self.output_dir = self.test_root / "output_files" / "network_io"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "test_output.gnf"

    def test_from_file_creates_network(self) -> None:
        """Test that from_file() creates a populated network."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        network = NetworkLV.from_file(str(self.input_file))

        self.assertIsInstance(network, NetworkLV)
        self.assertGreater(len(network.nodes), 0, "Network should contain nodes")
        self.assertGreater(len(network.cables), 0, "Network should contain cables")

    def test_from_file_with_path_object(self) -> None:
        """Test that from_file() accepts Path objects."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        network = NetworkLV.from_file(self.input_file)

        self.assertIsInstance(network, NetworkLV)
        self.assertGreater(len(network.nodes), 0)

    def test_save_creates_file(self) -> None:
        """Test that save() creates a valid GNF file."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        network = NetworkLV.from_file(self.input_file)
        network.save(str(self.output_file))

        self.assertTrue(self.output_file.exists(), "Output file should be created")
        self.assertGreater(
            self.output_file.stat().st_size,
            0,
            "Output file should not be empty",
        )

    def test_save_with_path_object(self) -> None:
        """Test that save() accepts Path objects."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        network = NetworkLV.from_file(self.input_file)
        network.save(self.output_file)

        self.assertTrue(self.output_file.exists())

    def test_roundtrip_preserves_data(self) -> None:
        """Test that load -> save -> load preserves network data."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        # Load original
        network1 = NetworkLV.from_file(self.input_file)
        original_node_count = len(network1.nodes)
        original_cable_count = len(network1.cables)

        # Save and reload
        network1.save(self.output_file)
        network2 = NetworkLV.from_file(self.output_file)

        # Verify counts match
        self.assertEqual(
            len(network2.nodes),
            original_node_count,
            "Node count should be preserved",
        )
        self.assertEqual(
            len(network2.cables),
            original_cable_count,
            "Cable count should be preserved",
        )


class TestNetworkMVIO(unittest.TestCase):
    """Test NetworkMV.from_file() and save() methods."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.test_root = Path(__file__).parent
        self.input_file = self.test_root / "input_files" / "AllComponents.vnf"
        self.output_dir = self.test_root / "output_files" / "network_io"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "test_output.vnf"

    def test_from_file_creates_network(self) -> None:
        """Test that from_file() creates a populated network."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        network = NetworkMV.from_file(str(self.input_file))

        self.assertIsInstance(network, NetworkMV)
        self.assertGreater(len(network.nodes), 0, "Network should contain nodes")
        self.assertGreater(len(network.cables), 0, "Network should contain cables")

    def test_from_file_with_path_object(self) -> None:
        """Test that from_file() accepts Path objects."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        network = NetworkMV.from_file(self.input_file)

        self.assertIsInstance(network, NetworkMV)
        self.assertGreater(len(network.nodes), 0)

    def test_save_creates_file(self) -> None:
        """Test that save() creates a valid VNF file."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        network = NetworkMV.from_file(self.input_file)
        network.save(str(self.output_file))

        self.assertTrue(self.output_file.exists(), "Output file should be created")
        self.assertGreater(
            self.output_file.stat().st_size,
            0,
            "Output file should not be empty",
        )

    def test_save_with_path_object(self) -> None:
        """Test that save() accepts Path objects."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        network = NetworkMV.from_file(self.input_file)
        network.save(self.output_file)

        self.assertTrue(self.output_file.exists())

    def test_roundtrip_preserves_data(self) -> None:
        """Test that load -> save -> load preserves network data."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.vnf not found")

        # Load original
        network1 = NetworkMV.from_file(self.input_file)
        original_node_count = len(network1.nodes)
        original_cable_count = len(network1.cables)

        # Save and reload
        network1.save(self.output_file)
        network2 = NetworkMV.from_file(self.output_file)

        # Verify counts match
        self.assertEqual(
            len(network2.nodes),
            original_node_count,
            "Node count should be preserved",
        )
        self.assertEqual(
            len(network2.cables),
            original_cable_count,
            "Cable count should be preserved",
        )


class TestNetworkImportFromPackage(unittest.TestCase):
    """Test that NetworkLV and NetworkMV can be imported from pyptp."""

    def test_import_network_lv_from_pyptp(self) -> None:
        """Test importing NetworkLV from top-level pyptp package."""
        from pyptp import NetworkLV as ImportedNetworkLV

        network = ImportedNetworkLV()
        self.assertIsInstance(network, ImportedNetworkLV)

    def test_import_network_mv_from_pyptp(self) -> None:
        """Test importing NetworkMV from top-level pyptp package."""
        from pyptp import NetworkMV as ImportedNetworkMV

        network = ImportedNetworkMV()
        self.assertIsInstance(network, ImportedNetworkMV)


if __name__ == "__main__":
    unittest.main()
