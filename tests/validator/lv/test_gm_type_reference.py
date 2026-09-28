from __future__ import annotations

import unittest

from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.gm_type import GMTypeLV
from pyptp.network_lv import NetworkLV
from pyptp.validator.lv.gm_type_reference import GMTypeReferenceValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestGMTypeReferenceLV(unittest.TestCase):
    """LV GM type reference validation."""

    def _network(
        self, *gm_type_numbers: int, registered: tuple[int, ...] = ()
    ) -> NetworkLV:
        network = NetworkLV()
        for number in registered:
            network.add(
                GMTypeLV(general=GMTypeLV.General(number=number, type=f"sjv{number}"))
            )
        network.add(
            ConnectionLV(
                general=ConnectionLV.General(name="Woning"),
                presentations=[],
                gms=[
                    ConnectionLV.GM(gm_type_number=number, p=0.001)
                    for number in gm_type_numbers
                ],
            )
        )
        return network

    def test_known_gm_type_no_issues(self) -> None:
        network = self._network(3, registered=(3,))

        assert_no_validation_issues(self, GMTypeReferenceValidator(), network)

    def test_unknown_gm_type_reports_error(self) -> None:
        network = self._network(7, registered=(3,))

        issues = GMTypeReferenceValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "unknown_gm_type")
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["gm_type_number"], 7)

    def test_gm_type_number_0_is_reported(self) -> None:
        network = self._network(0, registered=(3,))

        issues = GMTypeReferenceValidator().validate(network)
        self.assertEqual([issue.code for issue in issues], ["unknown_gm_type"])

    def test_connection_without_gms_no_issues(self) -> None:
        network = self._network(registered=(3,))

        assert_no_validation_issues(self, GMTypeReferenceValidator(), network)

    def test_one_issue_per_unknown_gm(self) -> None:
        network = self._network(7, 3, 9, registered=(3,))

        issues = GMTypeReferenceValidator().validate(network)
        details = [issue.details for issue in issues]
        self.assertEqual(
            details, [{"gm": 1, "gm_type_number": 7}, {"gm": 3, "gm_type_number": 9}]
        )


if __name__ == "__main__":
    unittest.main()
