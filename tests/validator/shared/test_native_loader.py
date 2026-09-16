"""Tests for the native loader validator."""

from __future__ import annotations

import unittest

from pyptp import NetworkLV, NetworkMV
from pyptp.convert.version_migrator import ERR_LOAD_FAILURE, NativeResult
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.validator import CheckRunner, Severity, ValidatorCategory
from pyptp.validator.shared.native_loader import (
    NativeLoaderValidator,
    issues_from_native_result,
)
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestNativeLoaderValidator(unittest.TestCase):
    def test_empty_mv_network_has_no_issues(self) -> None:
        assert_no_validation_issues(self, NativeLoaderValidator(), NetworkMV())

    def test_empty_lv_network_has_no_issues(self) -> None:
        assert_no_validation_issues(self, NativeLoaderValidator(), NetworkLV())

    def test_rejected_object_is_reported_with_type_and_guid(self) -> None:
        network = NetworkMV()
        field = MeasureFieldMV(general=MeasureFieldMV.General(), presentations=[])
        field.register(network)

        issues = NativeLoaderValidator().validate(network)

        self.assertEqual(len(issues), 1)
        issue = issues[0]
        self.assertEqual(issue.code, "native_load_error")
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.object_type, "Meetveld")
        self.assertEqual(issue.object_id, field.general.guid)
        self.assertEqual(issue.validator, "native_loader")
        self.assertIn("in-object niet toegekend", issue.message)

    def test_runs_by_default_but_not_as_core(self) -> None:
        network = NetworkMV()
        MeasureFieldMV(general=MeasureFieldMV.General(), presentations=[]).register(
            network
        )
        runner = CheckRunner(network)

        default_report = runner.run()
        core_report = runner.run(categories=ValidatorCategory.CORE)

        self.assertTrue(
            any(i.validator == "native_loader" for i in default_report.issues)
        )
        self.assertFalse(
            any(i.validator == "native_loader" for i in core_report.issues)
        )


class TestIssuesFromNativeResult(unittest.TestCase):
    def test_file_level_message_has_no_object(self) -> None:
        result = NativeResult(
            code=ERR_LOAD_FAILURE,
            errors=["Fout bij het openen van x.vnf."],
            warnings=["let op"],
        )

        issues = issues_from_native_result(result, "native_loader")

        self.assertEqual(
            [i.severity for i in issues], [Severity.ERROR, Severity.WARNING]
        )
        self.assertEqual(issues[0].object_type, "Network")
        self.assertIsNone(issues[0].object_id)
        self.assertEqual(issues[1].code, "native_load_warning")
        self.assertEqual(issues[1].details, {"native_code": ERR_LOAD_FAILURE})


if __name__ == "__main__":
    unittest.main()
