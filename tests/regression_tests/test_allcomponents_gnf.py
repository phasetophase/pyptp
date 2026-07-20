"""Individual regression test for AllComponents.gnf import/export functionality."""

import re
import unittest
from pathlib import Path

from pyptp import NetworkLV


class TestAllComponentsGnfRegression(unittest.TestCase):
    """Individual regression test for AllComponents.gnf."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents.gnf"
        self.output_dir = self.root / "output_files" / "regression_individual"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "AllComponents_exported.gnf"

    def _count_section_lines(self, content: str, section_name: str) -> int:
        """Count lines in a specific section."""
        pattern = rf"\[{re.escape(section_name)}\]\n(.*?)\n\[\]"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return 0
        section_content = match.group(1).strip()
        if not section_content:
            return 0
        return len([line for line in section_content.split("\n") if line.strip()])

    def _get_section_content(self, content: str, section_name: str) -> str:
        """Extract content of a specific section."""
        pattern = rf"\[{re.escape(section_name)}\]\n(.*?)\n\[\]"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def test_allcomponents_gnf_roundtrip(self) -> None:
        """Test full round-trip import/export for AllComponents.gnf."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        # Read original file
        original_content = self.input_file.read_text(encoding="utf-8-sig")

        # Import and export
        network = NetworkLV.from_file(self.input_file)
        network.save(self.output_file)

        # Read exported file
        exported_content = self.output_file.read_text(encoding="utf-8")

        # Compare line counts for each section
        sections = [
            "PROPERTIES",
            "COMMENTS",
            "PROFILEFILES",
            "MEASUREMENTFILES",
            "GM TYPE",
            "SHEET",
            "NODE",
            "LINK",
            "CABLE",
            "TRANSFORMER",
            "SPECIAL TRANSFORMER",
            "REACTANCECOIL",
            "SOURCE",
            "SYNCHRONOUS GENERATOR",
            "ASYNCHRONOUS GENERATOR",
            "ASYNCHRONOUS MOTOR",
            "LOAD",
            "SHUNTCAPACITOR",
            "EARTHINGTRANSFORMER",
            "HOME",
            "BATTERY",
            "PV",
            "FUSE",
            "CIRCUIT BREAKER",
            "SELECTION",
        ]

        for section in sections:
            original_lines = self._count_section_lines(original_content, section)
            exported_lines = self._count_section_lines(exported_content, section)
            self.assertEqual(
                original_lines,
                exported_lines,
                f"Section [{section}] line count mismatch: "
                f"original={original_lines}, exported={exported_lines}",
            )

    def test_properties_section_roundtrip(self) -> None:
        """Test PROPERTIES section preserves all sub-sections."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        original_content = self.input_file.read_text(encoding="utf-8-sig")
        network = NetworkLV.from_file(self.input_file)
        network.save(self.output_file)
        exported_content = self.output_file.read_text(encoding="utf-8")

        original_props = self._get_section_content(original_content, "PROPERTIES")
        exported_props = self._get_section_content(exported_content, "PROPERTIES")

        # Verify all sub-sections are present
        subsections = [
            "#System",
            "#Network",
            "#General",
            "#Invisible",
            "#History",
            "#HistoryItems",
            "#Users",
        ]
        for subsection in subsections:
            self.assertIn(
                subsection,
                original_props,
                f"{subsection} missing from original PROPERTIES",
            )
            self.assertIn(
                subsection,
                exported_props,
                f"{subsection} missing from exported PROPERTIES",
            )

        # Verify currency is preserved
        self.assertIn(
            "Currency:'€'", exported_props, "Currency not preserved in export"
        )

    def test_comments_section_roundtrip(self) -> None:
        """Test COMMENTS section preserves all comments."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        original_content = self.input_file.read_text(encoding="utf-8-sig")
        network = NetworkLV.from_file(self.input_file)

        original_comments = self._get_section_content(original_content, "COMMENTS")
        original_comment_count = original_comments.count("#Comment")

        # Verify comments were imported
        self.assertEqual(
            len(network.comments),
            original_comment_count,
            f"Comments import mismatch: expected {original_comment_count}, got {len(network.comments)}",
        )

        # Export and verify
        network.save(self.output_file)
        exported_content = self.output_file.read_text(encoding="utf-8")
        exported_comments = self._get_section_content(exported_content, "COMMENTS")
        exported_comment_count = exported_comments.count("#Comment")

        self.assertEqual(
            original_comment_count,
            exported_comment_count,
            f"Comments export mismatch: expected {original_comment_count}, got {exported_comment_count}",
        )

    def test_node_count_matches(self) -> None:
        """Test node count matches between import and original file."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        original_content = self.input_file.read_text(encoding="utf-8-sig")
        network = NetworkLV.from_file(self.input_file)

        # Count #General lines in NODE section (each node starts with #General)
        node_section = self._get_section_content(original_content, "NODE")
        original_node_count = node_section.count("#General")

        self.assertEqual(
            len(network.nodes),
            original_node_count,
            f"Node count mismatch: expected {original_node_count}, got {len(network.nodes)}",
        )

    def test_cable_count_matches(self) -> None:
        """Test cable count matches between import and original file."""
        if not self.input_file.exists():
            self.skipTest("AllComponents.gnf not found")

        original_content = self.input_file.read_text(encoding="utf-8-sig")
        network = NetworkLV.from_file(self.input_file)

        cable_section = self._get_section_content(original_content, "CABLE")
        original_cable_count = cable_section.count("#General")

        self.assertEqual(
            len(network.cables),
            original_cable_count,
            f"Cable count mismatch: expected {original_cable_count}, got {len(network.cables)}",
        )


class TestAllComponentsV812GnfRegression(unittest.TestCase):
    """Individual regression test for AllComponents_v812.gnf (native Gaia 8.12 save)."""

    def setUp(self) -> None:
        """Set up test paths and ensure output directory exists."""
        self.root = Path(__file__).parent.parent
        self.input_file = self.root / "input_files" / "AllComponents_v812.gnf"
        self.output_dir = self.root / "output_files" / "regression_individual"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "AllComponents_v812_exported.gnf"

    def _count_section_lines(self, content: str, section_name: str) -> int:
        """Count lines in a specific section."""
        pattern = rf"\[{re.escape(section_name)}\]\n(.*?)\n\[\]"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return 0
        section_content = match.group(1).strip()
        if not section_content:
            return 0
        return len([line for line in section_content.split("\n") if line.strip()])

    def test_allcomponents_v812_gnf_roundtrip(self) -> None:
        """Test full round-trip import/export for AllComponents_v812.gnf."""
        if not self.input_file.exists():
            self.skipTest("AllComponents_v812.gnf not found")

        original_content = self.input_file.read_text(encoding="utf-8-sig")

        network = NetworkLV.from_file(self.input_file)
        network.save(self.output_file)

        exported_content = self.output_file.read_text(encoding="utf-8")

        sections = [
            "PROPERTIES",
            "COMMENTS",
            "PROFILEFILES",
            "MEASUREMENTFILES",
            "GM TYPE",
            "SHEET",
            "NODE",
            "LINK",
            "CABLE",
            "TRANSFORMER",
            "SPECIAL TRANSFORMER",
            "REACTANCECOIL",
            "SOURCE",
            "SYNCHRONOUS GENERATOR",
            "ASYNCHRONOUS GENERATOR",
            "ASYNCHRONOUS MOTOR",
            "LOAD",
            "SHUNTCAPACITOR",
            "EARTHINGTRANSFORMER",
            "HOME",
            "BATTERY",
            "PV",
            "MEASURE FIELD",
            "FUSE",
            "CIRCUIT BREAKER",
            "LOAD SWITCH",
            "SELECTION",
        ]

        for section in sections:
            original_lines = self._count_section_lines(original_content, section)
            exported_lines = self._count_section_lines(exported_content, section)
            self.assertGreater(
                original_lines,
                0,
                f"Section [{section}] missing or empty in input file",
            )
            self.assertEqual(
                original_lines,
                exported_lines,
                f"Section [{section}] line count mismatch: "
                f"original={original_lines}, exported={exported_lines}",
            )

    def test_battery_812_controls_roundtrip(self) -> None:
        """Test battery P(U)/P(I) controls survive the round trip with MeasureField reference."""
        if not self.input_file.exists():
            self.skipTest("AllComponents_v812.gnf not found")

        network = NetworkLV.from_file(self.input_file)
        network.save(self.output_file)
        exported_content = self.output_file.read_text(encoding="utf-8")

        battery = next(iter(network.batteries.values()))
        assert battery.pu_control is not None
        assert battery.pi_control is not None
        measure_field = next(iter(network.measure_fields.values()))
        self.assertEqual(battery.pi_control.measure_field1, measure_field.general.guid)

        self.assertIn("#P(U)Control", exported_content)
        self.assertIn(
            "MeasureField1:'{32724952-E706-4340-A9B2-A26C334BF320}'",
            exported_content,
        )


if __name__ == "__main__":
    unittest.main()
