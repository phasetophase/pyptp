from __future__ import annotations

import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

from pyptp.network_lv import NetworkLV
from pyptp.validator import CheckRunner, Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class CrashValidator(Validator):
    """Test double that raises to exercise crash reporting."""

    name = "_crash"
    description = "Test validator that crashes"
    applies_to = ("LV",)
    categories = ValidatorCategory.ALL  # Part of ALL but will crash

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        raise RuntimeError("deliberate failure")


class SucceedsValidator(Validator):
    """Test double that emits a single informational issue."""

    name = "_ok"
    description = "Test validator that succeeds"
    applies_to = ("LV",)
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        return [
            Issue(
                code="ok",
                message="success validator executed",
                severity=Severity.WARNING,
                object_type="network",
                object_id="-",
                validator=self.name,
            ),
        ]


class TestRunner(unittest.TestCase):
    def test_include_exclude_and_crash_handling(self) -> None:
        """CheckRunner honours include/exclude lists and records crashes."""
        low_voltage_network = NetworkLV()

        with patch(
            "pyptp.validator.runner.discover_validators",
            return_value=[CrashValidator, SucceedsValidator],
        ):
            runner = CheckRunner(low_voltage_network, "LV")

            report = runner.run(include=["_ok"])
            issue_codes = {issue.code for issue in report.issues}
            self.assertEqual(issue_codes, {"ok"})

            crash_report = runner.run(exclude=["_ok"])
            crash_codes = {issue.code for issue in crash_report.issues}
            self.assertEqual(crash_codes, {"validator_crash"})

    def test_list_available_returns_validator_metadata(self) -> None:
        """CheckRunner.list_available() returns metadata for each validator."""
        low_voltage_network = NetworkLV()

        with patch(
            "pyptp.validator.runner.discover_validators",
            return_value=[SucceedsValidator],
        ):
            runner = CheckRunner(low_voltage_network, "LV")
            available = runner.list_available()

            self.assertEqual(len(available), 1)
            self.assertEqual(available[0]["name"], "_ok")
            self.assertEqual(
                available[0]["description"], "Test validator that succeeds"
            )
            self.assertIn("applies_to", available[0])
            self.assertIsInstance(available[0]["applies_to"], tuple)

    def test_validator_missing_required_fields(self) -> None:
        """Validators without required fields raise TypeError at class definition."""
        with self.assertRaises(TypeError) as ctx:

            class NoNameValidator(Validator):
                """Missing name field."""

                description = "Test"
                applies_to = ("LV",)
                categories = ValidatorCategory.ALL

                def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
                    return []

        self.assertIn("must define 'name'", str(ctx.exception))

        with self.assertRaises(TypeError) as ctx:

            class NoDescriptionValidator(Validator):
                """Missing description field."""

                name = "test"
                applies_to = ("LV",)
                categories = ValidatorCategory.ALL

                def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
                    return []

        self.assertIn("must define 'description'", str(ctx.exception))

        with self.assertRaises(TypeError) as ctx:

            class NoAppliesToValidator(Validator):
                """Missing applies_to field."""

                name = "test"
                description = "Test"
                categories = ValidatorCategory.ALL

                def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
                    return []

        self.assertIn("must define 'applies_to'", str(ctx.exception))

    def test_validator_applies_to_duplicates(self) -> None:
        """Validators with duplicate applies_to values raise ValueError."""
        with self.assertRaises(ValueError) as ctx:

            class DuplicateAppliesToValidator(Validator):
                """Has duplicate applies_to values."""

                name = "test"
                description = "Test"
                applies_to = ("LV", "LV")
                categories = ValidatorCategory.ALL

                def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
                    return []

        self.assertIn("contains duplicate values", str(ctx.exception))

    def test_category_filtering_core_only(self) -> None:
        """CheckRunner can filter validators by category."""
        # Note: Currently CORE == ALL, so this test verifies the filtering mechanism works
        # When more categories are added, this test will need adjustment
        low_voltage_network = NetworkLV()

        with patch(
            "pyptp.validator.runner.discover_validators",
            return_value=[SucceedsValidator],
        ):
            runner = CheckRunner(low_voltage_network, "LV")

            # Run CORE validators
            report = runner.run(categories=ValidatorCategory.CORE)
            issue_codes = {issue.code for issue in report.issues}
            self.assertEqual(issue_codes, {"ok"})

    def test_category_filtering_all(self) -> None:
        """CheckRunner with ALL category runs all validators."""
        low_voltage_network = NetworkLV()

        with patch(
            "pyptp.validator.runner.discover_validators",
            return_value=[SucceedsValidator],
        ):
            runner = CheckRunner(low_voltage_network, "LV")

            # Default ALL should run everything
            report = runner.run()
            self.assertEqual(len(report.issues), 1)

            # Explicit ALL should also run everything
            report = runner.run(categories=ValidatorCategory.ALL)
            self.assertEqual(len(report.issues), 1)

    def test_auto_detect_network_type_lv(self) -> None:
        """CheckRunner auto-detects LV network type from NetworkLV class."""
        low_voltage_network = NetworkLV()

        with patch(
            "pyptp.validator.runner.discover_validators",
            return_value=[SucceedsValidator],
        ):
            runner = CheckRunner(low_voltage_network)  # No network_type specified
            self.assertEqual(runner.network_type, "LV")

    def test_auto_detect_network_type_mv(self) -> None:
        """CheckRunner auto-detects MV network type from NetworkMV class."""
        from pyptp.network_mv import NetworkMV

        medium_voltage_network = NetworkMV()

        with patch("pyptp.validator.runner.discover_validators", return_value=[]):
            runner = CheckRunner(medium_voltage_network)  # No network_type specified
            self.assertEqual(runner.network_type, "MV")

    def test_explicit_network_type_overrides_auto_detect(self) -> None:
        """Explicitly provided network_type is used even if auto-detection would work."""
        low_voltage_network = NetworkLV()

        with patch("pyptp.validator.runner.discover_validators", return_value=[]):
            runner = CheckRunner(low_voltage_network, network_type="MV")
            self.assertEqual(runner.network_type, "MV")

    def test_auto_detect_fails_for_unknown_class(self) -> None:
        """CheckRunner raises ValueError if network type cannot be auto-detected."""

        class UnknownNetwork:
            """Network class that doesn't match LV/MV/LS/MS pattern."""

        unknown_network = UnknownNetwork()

        with patch("pyptp.validator.runner.discover_validators", return_value=[]):
            with self.assertRaises(ValueError) as ctx:
                CheckRunner(unknown_network)  # type: ignore[arg-type]

            self.assertIn("Cannot auto-detect network type", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
