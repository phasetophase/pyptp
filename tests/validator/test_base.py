from __future__ import annotations

import json
import unittest

from pyptp.validator import Issue, Report, Severity


class TestValidatorBase(unittest.TestCase):
    """Ensure Issue/Report helpers provide stable serialization."""

    def test_issue_and_report_serialization(self) -> None:
        issue = Issue(
            code="missing_node_reference",
            message="Cable references unknown node",
            severity=Severity.ERROR,
            object_type="Cable",
            object_id="oid",
            validator="cable_node_reference",
            details={"endpoint": "node1"},
        )
        report = Report(issues=[issue])

        serialized_dict = report.to_dict()
        self.assertIn("issues", serialized_dict)
        self.assertEqual(serialized_dict["issues"][0]["code"], "missing_node_reference")

        serialized_json = report.to_json()
        parsed_json = json.loads(serialized_json)
        self.assertEqual(parsed_json["issues"][0]["validator"], "cable_node_reference")

    def test_report_summary_no_issues(self) -> None:
        """Report with no issues shows 'No issues found'."""
        report = Report(issues=[])
        self.assertEqual(report.summary(), "No issues found")

    def test_report_summary_single_issue(self) -> None:
        """Report with single issue uses singular 'issue'."""
        issue = Issue(
            code="test",
            message="test message",
            severity=Severity.ERROR,
            object_type="Test",
            object_id="test_id",
            validator="test_validator",
        )
        report = Report(issues=[issue])
        self.assertEqual(report.summary(), "Found 1 issue: 1 error")

    def test_report_summary_multiple_errors(self) -> None:
        """Report with multiple errors of same severity."""
        issues = [
            Issue(
                code="test1",
                message="test1",
                severity=Severity.ERROR,
                object_type="Test",
                object_id="id1",
                validator="test",
            ),
            Issue(
                code="test2",
                message="test2",
                severity=Severity.ERROR,
                object_type="Test",
                object_id="id2",
                validator="test",
            ),
        ]
        report = Report(issues=issues)
        self.assertEqual(report.summary(), "Found 2 issues: 2 error")

    def test_report_summary_mixed_severities(self) -> None:
        """Report with both errors and warnings."""
        issues = [
            Issue(
                code="e1",
                message="error1",
                severity=Severity.ERROR,
                object_type="Test",
                object_id="id1",
                validator="test",
            ),
            Issue(
                code="e2",
                message="error2",
                severity=Severity.ERROR,
                object_type="Test",
                object_id="id2",
                validator="test",
            ),
            Issue(
                code="w1",
                message="warning1",
                severity=Severity.WARNING,
                object_type="Test",
                object_id="id3",
                validator="test",
            ),
        ]
        report = Report(issues=issues)
        self.assertEqual(report.summary(), "Found 3 issues: 2 error, 1 warning")


if __name__ == "__main__":
    unittest.main()
