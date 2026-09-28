from __future__ import annotations

import unittest

from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.source import SourceLV
from pyptp.network_lv import NetworkLV
from pyptp.validator.lv.source_voltage import SourceVoltageValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestSourceVoltageLV(unittest.TestCase):
    """LV source voltage validation."""

    def _network(self, unom: float, umin: float, umax: float) -> NetworkLV:
        network = NetworkLV()
        node = network.add(
            NodeLV(general=NodeLV.General(name="Rail", unom=unom), presentations=[])
        )
        network.add(
            SourceLV(
                general=SourceLV.General(
                    name="Voeding",
                    node=node.general.guid,
                    umin=umin,
                    umax=umax,
                    uref=umin,
                ),
                presentations=[],
            )
        )
        return network

    def _codes(self, network: NetworkLV) -> list[str]:
        return [issue.code for issue in SourceVoltageValidator().validate(network)]

    def test_matching_voltage_no_issues(self) -> None:
        network = self._network(0.4, umin=0.4, umax=0.4)

        assert_no_validation_issues(self, SourceVoltageValidator(), network)

    def test_default_source_on_mv_node_reports_umin(self) -> None:
        network = NetworkLV()
        node = network.add(
            NodeLV(general=NodeLV.General(name="Rail", unom=10.0), presentations=[])
        )
        network.add(
            SourceLV(
                general=SourceLV.General(name="Voeding", node=node.general.guid),
                presentations=[],
            )
        )

        issues = SourceVoltageValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "source_umin_out_of_range")
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["lower"], 5.0)

    def test_umin_above_upper_bound_reports_umin(self) -> None:
        network = self._network(0.4, umin=0.7, umax=0.7)

        self.assertEqual(self._codes(network), ["source_umin_out_of_range"])

    def test_umax_above_upper_bound_reports_umax(self) -> None:
        network = self._network(0.4, umin=0.4, umax=0.8)

        self.assertEqual(self._codes(network), ["source_umax_out_of_range"])

    def test_umax_below_umin_reports_umax(self) -> None:
        network = self._network(0.4, umin=0.4, umax=0.3)

        self.assertEqual(self._codes(network), ["source_umax_out_of_range"])

    def test_bounds_are_inclusive(self) -> None:
        network = self._network(0.4, umin=0.2, umax=0.6)

        assert_no_validation_issues(self, SourceVoltageValidator(), network)

    def test_umin_just_below_lower_bound_reports_umin(self) -> None:
        network = self._network(0.41, umin=0.201, umax=0.41)

        issues = SourceVoltageValidator().validate(network)
        self.assertEqual([issue.code for issue in issues], ["source_umin_out_of_range"])
        self.assertIn("0.205", issues[0].message)

    def test_umax_just_above_upper_bound_reports_umax(self) -> None:
        network = self._network(0.23, umin=0.23, umax=0.346)

        self.assertEqual(self._codes(network), ["source_umax_out_of_range"])

    def test_umin_within_tolerance_of_lower_bound_passes(self) -> None:
        network = self._network(0.4, umin=0.2 * (1 - 1e-9), umax=0.4)

        assert_no_validation_issues(self, SourceVoltageValidator(), network)

    def test_umin_and_umax_both_wrong_report_umin_only(self) -> None:
        network = self._network(10.0, umin=0.4, umax=0.3)

        self.assertEqual(self._codes(network), ["source_umin_out_of_range"])

    def test_source_without_node_is_skipped(self) -> None:
        network = NetworkLV()
        network.add(SourceLV(general=SourceLV.General(name="Los"), presentations=[]))

        assert_no_validation_issues(self, SourceVoltageValidator(), network)


if __name__ == "__main__":
    unittest.main()
