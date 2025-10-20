"""Individual regression test for AllComponents.gnf import/export functionality."""

import unittest
from pathlib import Path

from pyptp import NetworkLV
from pyptp.ptp_log import logger


class TestAllComponentsGnfRegression(unittest.TestCase):
    """Individual regression test for AllComponents.gnf."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents.gnf"
        self.output_dir = self.root / "output_files" / "regression_individual"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "AllComponents_exported.gnf"
        self.logger = logger

    def test_allcomponents_gnf_import_export(self) -> None:
        """Test import/export for AllComponents.gnf."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        try:
            # Import the network
            network = NetworkLV.from_file(str(self.input_file))

            # Export the network
            network.save(str(self.output_file))

            # Verify the output file
            self.assertTrue(
                self.output_file.exists(),
                f"Output file {self.output_file!s} was not created",
            )
            file_size = self.output_file.stat().st_size
            self.assertGreater(file_size, 0, "Export file should not be empty")

            # Validate network components
            self.assertGreater(len(network.nodes), 0, "Network should contain nodes")
            self.assertGreater(len(network.cables), 0, "Network should contain cables")

        except (OSError, ValueError) as e:
            self.fail(f"Failed to import/export AllComponents.gnf: {e!s}")


if __name__ == "__main__":
    unittest.main()
