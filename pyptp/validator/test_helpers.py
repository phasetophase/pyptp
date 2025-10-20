"""Shared test helpers for validator tests.

These helpers eliminate boilerplate assertion code that's repeated across
reference validator tests (cable, link, transformer).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest import TestCase

    from pyptp.elements.element_utils import Guid
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV
    from pyptp.validator import Validator


def assert_no_validation_issues(
    test_case: TestCase,
    validator: Validator,
    network: NetworkLV | NetworkMV,
) -> None:
    """Assert that validator finds no issues in the network.

    Args:
        test_case: unittest.TestCase instance for assertions
        validator: Validator instance to run
        network: Network to validate

    """
    issues = validator.validate(network)
    test_case.assertEqual(issues, [])


def assert_missing_node_reference(
    test_case: TestCase,
    validator: Validator,
    network: NetworkLV | NetworkMV,
    expected_end: str,
    expected_guid: Guid,
) -> None:
    """Assert that validator reports exactly one missing node reference issue.

    Verifies:
    - Exactly 1 issue is reported
    - Issue has details dictionary
    - Details contains correct endpoint name
    - Details contains expected missing GUID

    Args:
        test_case: unittest.TestCase instance for assertions
        validator: Validator instance to run
        network: Network to validate
        expected_end: Expected endpoint name ("node1" or "node2")
        expected_guid: Expected GUID that's missing from the network

    """
    issues = validator.validate(network)
    test_case.assertEqual(len(issues), 1)
    test_case.assertIsNotNone(issues[0].details)

    details = issues[0].details or {}
    test_case.assertEqual(details["which_end"], expected_end)
    test_case.assertEqual(details.get("referenced_guid"), expected_guid)


def assert_issue_count(
    test_case: TestCase,
    validator: Validator,
    network: NetworkLV | NetworkMV,
    expected_count: int,
) -> None:
    """Assert that validator finds exactly the expected number of issues.

    Args:
        test_case: unittest.TestCase instance for assertions
        validator: Validator instance to run
        network: Network to validate
        expected_count: Expected number of issues

    """
    issues = validator.validate(network)
    test_case.assertEqual(len(issues), expected_count)
