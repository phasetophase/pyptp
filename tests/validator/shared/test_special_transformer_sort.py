from __future__ import annotations

import unittest

from pyptp.elements.element_utils import Guid
from pyptp.elements.enums import SpecialTransformerSort
from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator import Severity
from pyptp.validator.shared.special_transformer_sort import (
    SpecialTransformerSortValidator,
)
from pyptp.validator.test_helpers import (
    assert_issue_count,
    assert_no_validation_issues,
)


def _make_lv(sort: SpecialTransformerSort) -> tuple[NetworkLV, Guid]:
    network = NetworkLV()
    general = SpecialTransformerLV.General(name="ST1")
    stype = SpecialTransformerLV.SpecialTransformerType(short_name="T", sort=sort)
    element = SpecialTransformerLV(general=general, presentations=[], type=stype)
    element.register(network)
    return network, general.guid


def _make_mv(sort: SpecialTransformerSort) -> tuple[NetworkMV, Guid]:
    network = NetworkMV()
    general = SpecialTransformerMV.General(name="ST1")
    stype = SpecialTransformerMV.SpecialTransformerType(short_name="T", sort=sort)
    element = SpecialTransformerMV(general=general, presentations=[], type=stype)
    element.register(network)
    return network, general.guid


class TestSpecialTransformerSortLV(unittest.TestCase):
    def test_valid_sort_reports_no_issues(self) -> None:
        network, _ = _make_lv(SpecialTransformerSort.AUTO_YD11)
        assert_no_validation_issues(self, SpecialTransformerSortValidator(), network)

    def test_none_sort_reports_error(self) -> None:
        network, guid = _make_lv(SpecialTransformerSort.NONE)
        validator = SpecialTransformerSortValidator()
        assert_issue_count(self, validator, network, 1)

        issue = validator.validate(network)[0]
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.object_type, "SpecialTransformer")
        self.assertEqual(issue.object_id, guid)
        self.assertEqual(issue.code, "special_transformer_sort_none")


class TestSpecialTransformerSortMV(unittest.TestCase):
    def test_valid_sort_reports_no_issues(self) -> None:
        network, _ = _make_mv(SpecialTransformerSort.AUTO_YD11)
        assert_no_validation_issues(self, SpecialTransformerSortValidator(), network)

    def test_none_sort_reports_error(self) -> None:
        network, guid = _make_mv(SpecialTransformerSort.NONE)
        validator = SpecialTransformerSortValidator()
        assert_issue_count(self, validator, network, 1)

        issue = validator.validate(network)[0]
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.object_type, "SpecialTransformer")
        self.assertEqual(issue.object_id, guid)
        self.assertEqual(issue.code, "special_transformer_sort_none")

    def test_empty_network_reports_no_issues(self) -> None:
        network = NetworkMV()
        assert_no_validation_issues(self, SpecialTransformerSortValidator(), network)


if __name__ == "__main__":
    unittest.main()
