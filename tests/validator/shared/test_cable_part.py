from __future__ import annotations

import unittest

from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.shared import CableType as CableTypeLV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.shared import CableType as CableTypeMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.cable_part import CablePartValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestCablePartLV(unittest.TestCase):
    """LV cable part validation."""

    def _cable(self, length: float) -> CableLV:
        return CableLV(
            general=CableLV.General(name="Kabel"),
            presentations=[],
            cable_part=CableLV.CablePart(length=length, type="4x150 Al"),
            cable_type=CableTypeLV(short_name="150 Al"),
        )

    def test_valid_part_no_issues(self) -> None:
        network = NetworkLV()
        network.add(self._cable(15.0))

        assert_no_validation_issues(self, CablePartValidator(), network)

    def test_minimum_length_is_accepted(self) -> None:
        network = NetworkLV()
        network.add(self._cable(0.5))

        assert_no_validation_issues(self, CablePartValidator(), network)

    def test_length_within_tolerance_of_minimum_is_accepted(self) -> None:
        network = NetworkLV()
        network.add(self._cable(0.5 * (1 - 1e-9)))

        assert_no_validation_issues(self, CablePartValidator(), network)

    def test_part_below_minimum_reports_error(self) -> None:
        network = NetworkLV()
        network.add(self._cable(0.2))

        issues = CablePartValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "cable_part_too_short")
        self.assertIn("0.2 m", issues[0].message)
        self.assertEqual(issues[0].details, {"part": 1, "length": 0.2, "minimum": 0.5})

    def test_part_without_type_data_reports_error(self) -> None:
        network = NetworkLV()
        cable = self._cable(15.0)
        cable.cable_type = None
        network.add(cable)

        issues = CablePartValidator().validate(network)
        self.assertEqual([issue.code for issue in issues], ["cable_part_without_type"])

    def test_short_and_untyped_report_separately(self) -> None:
        network = NetworkLV()
        cable = self._cable(0.1)
        cable.cable_type = None
        network.add(cable)

        issues = CablePartValidator().validate(network)
        codes = [issue.code for issue in issues]
        self.assertEqual(codes, ["cable_part_too_short", "cable_part_without_type"])


class TestCablePartMV(unittest.TestCase):
    """MV cable part validation."""

    def _cable(self, *lengths: float, with_types: bool = True) -> CableMV:
        return CableMV(
            general=CableMV.General(name="Kabel"),
            presentations=[],
            cable_parts=[
                CableMV.CablePart(length=length, cable_type="GPLK 3x95")
                for length in lengths
            ],
            cable_types=[CableTypeMV(short_name="95 Cu") for _ in lengths]
            if with_types
            else [],
        )

    def test_valid_parts_no_issues(self) -> None:
        network = NetworkMV()
        network.add(self._cable(120.0, 45.0))

        assert_no_validation_issues(self, CablePartValidator(), network)

    def test_part_below_minimum_reports_error(self) -> None:
        network = NetworkMV()
        cable = self._cable(120.0)
        # CableMV lengthens short parts on construction, so shorten it afterwards
        cable.cable_parts[0].length = 0.5
        network.add(cable)

        issues = CablePartValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "cable_part_too_short")
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["minimum"], 1.0)

    def test_part_without_type_data_reports_error(self) -> None:
        network = NetworkMV()
        network.add(self._cable(120.0, with_types=False))

        issues = CablePartValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "cable_part_without_type")

    def test_second_part_without_type_data_reports_error(self) -> None:
        network = NetworkMV()
        cable = self._cable(120.0, 45.0)
        cable.cable_types.pop()
        network.add(cable)

        issues = CablePartValidator().validate(network)
        self.assertEqual(len(issues), 1)
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["part"], 2)


if __name__ == "__main__":
    unittest.main()
