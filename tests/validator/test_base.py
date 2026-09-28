from __future__ import annotations

import json
import unittest

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.node import NodeMV
from pyptp.validator import Issue, Report, Severity, Validator, ValidatorCategory


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

    def test_report_json_writes_guid_object_id_as_string(self) -> None:
        guid = Guid("2A421727-0EA3-4544-9C58-ADB67DCEE36A")
        issue = Issue(
            code="native_load_error",
            message="rejected",
            severity=Severity.ERROR,
            object_type="Meetveld",
            object_id=guid,
            validator="native_loader",
        )

        parsed_json = json.loads(Report(issues=[issue]).to_json())

        self.assertEqual(parsed_json["issues"][0]["object_id"], str(guid))

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


class _Example(Validator):
    name = "example"
    description = "Example validator"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: object) -> list[Issue]:  # noqa: ARG002
        return []


class TestValidatorIssue(unittest.TestCase):
    """Validator.issue() fills the fields that follow from the validator and the element."""

    def test_fields_from_validator_and_element(self) -> None:
        node = NodeLV(general=NodeLV.General(name="Rail"), presentations=[])

        issue = _Example().issue(node, "no_voltage", "Node has no voltage", unom=0)

        self.assertEqual(issue.validator, "example")
        self.assertEqual(issue.object_type, "Node")
        self.assertEqual(issue.object_id, node.general.guid)
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.details, {"unom": 0})

    def test_object_type_is_the_same_for_lv_and_mv(self) -> None:
        node = NodeMV(general=NodeMV.General(), presentations=[])

        issue = _Example().issue(node, "code", "message")

        self.assertEqual(issue.object_type, "Node")

    def test_severity_and_no_details(self) -> None:
        node = NodeLV(general=NodeLV.General(), presentations=[])

        issue = _Example().issue(node, "code", "message", severity=Severity.WARNING)

        self.assertEqual(issue.severity, Severity.WARNING)
        self.assertIsNone(issue.details)


if __name__ == "__main__":
    unittest.main()
