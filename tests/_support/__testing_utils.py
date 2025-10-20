from __future__ import annotations

import difflib
import json
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    import unittest


def _dataclass_to_dict(obj: object) -> dict[str, object]:
    """Convert dataclass to nested dictionary for comparison analysis.

    Recursively transforms dataclass instances into plain Python containers
    to enable deep equality checks and JSON serialization for test validation.

    Args:
        obj: Dataclass instance to convert.

    Returns:
        Nested dictionary representation with all dataclass fields.

    Raises:
        TypeError: If obj is not a dataclass instance.

    """
    if not is_dataclass(obj):
        msg = "Expected dataclass instance"
        raise TypeError(msg)
    result: dict[str, object] = {}
    for fld in fields(obj):
        val = getattr(obj, fld.name)
        if is_dataclass(val):
            val = _dataclass_to_dict(val)
        elif isinstance(val, (list, tuple)):
            val = [_dataclass_to_dict(v) if is_dataclass(v) else v for v in val]
        elif isinstance(val, dict):
            val = {
                k: _dataclass_to_dict(v) if is_dataclass(v) else v
                for k, v in val.items()
            }
        result[fld.name] = val
    return result


NormalizeFn: TypeAlias = Callable[[dict[str, object]], dict[str, object]]
"""Function type for normalizing dictionary data before comparison."""


def assert_text_diff_equal(
    test_case: unittest.TestCase,
    expected: str,
    actual: str,
    expected_name: str = "expected",
    actual_name: str = "actual",
) -> None:
    """Assert multiline string equality with unified diff on failure.

    Args:
        test_case: Test case instance for assertion failure.
        expected: Reference string content.
        actual: Generated string content to validate.
        expected_name: Label for expected content in diff output.
        actual_name: Label for actual content in diff output.

    Raises:
        AssertionError: When strings differ, includes unified diff.

    """
    exp = expected.splitlines(keepends=True)
    act = actual.splitlines(keepends=True)
    if exp != act:
        diff = difflib.unified_diff(
            exp, act, fromfile=expected_name, tofile=actual_name
        )
        test_case.fail("\n" + "".join(diff))


def assert_dataclass_deep_equal(
    test_case: unittest.TestCase,
    obj1: object,
    obj2: object,
    *,
    normalize: NormalizeFn = lambda x: x,
    name1: str = "obj1",
    name2: str = "obj2",
) -> None:
    """Assert deep equality between dataclass structures with JSON diff output.

    Converts dataclass instances to normalized dictionaries and compares them
    using JSON serialization for clear diff visualization in test failures.

    Args:
        test_case: Test case instance for assertion failure.
        obj1: First dataclass instance to compare.
        obj2: Second dataclass instance to compare.
        normalize: Optional function to normalize dictionary before comparison.
        name1: Label for first object in diff output.
        name2: Label for second object in diff output.

    Raises:
        AssertionError: When dataclass structures differ, includes JSON diff.

    """
    d1 = normalize(_dataclass_to_dict(obj1))
    d2 = normalize(_dataclass_to_dict(obj2))
    if d1 != d2:
        j1 = json.dumps(d1, indent=2, sort_keys=True).splitlines(keepends=True)
        j2 = json.dumps(d2, indent=2, sort_keys=True).splitlines(keepends=True)
        diff = difflib.unified_diff(j1, j2, fromfile=name1, tofile=name2)
        test_case.fail("\n" + "".join(diff))
