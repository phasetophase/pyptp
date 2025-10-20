"""Individual regression test for AllComponents_withpv.vnf import/export functionality."""

import unittest
from pathlib import Path

from pyptp import NetworkMV
from pyptp.ptp_log import logger


class TestAllComponentsWithPvVnfRegression(unittest.TestCase):
    """Individual regression test for AllComponents_withpv.vnf."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents_withpv.vnf"
        self.output_dir = self.root / "output_files" / "regression_individual"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "AllComponents_withpv_exported.vnf"
        self.logger = logger

    def test_allcomponents_withpv_vnf_import_export(self) -> None:
        """Test import/export for AllComponents_withpv.vnf."""
        if not self.input_file.exists():
            self.skipTest("AllComponents_withpv.vnf not found")

        try:
            network = NetworkMV.from_file(str(self.input_file))
            network.save(str(self.output_file))

            self.assertTrue(
                self.output_file.exists(),
                f"Output file {self.output_file!s} was not created",
            )

        except (OSError, ValueError) as e:
            self.fail(f"Failed to import/export AllComponents_withpv.vnf: {e!s}")


if __name__ == "__main__":
    unittest.main()
