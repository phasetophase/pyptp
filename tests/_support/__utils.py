import difflib
import unittest


def assert_gnf_equal(
    testcase: unittest.TestCase,
    actual: str,
    expected: str,
    fromfile: str = "expected.gnf",
    tofile: str = "reexported.gnf",
) -> None:
    """Assert GNF content equality with detailed diff reporting on failure.

    Compares multi-line GNF file content and fails with unified diff output
    when differences are detected. Optimized for network file format validation.

    Args:
        testcase: Test case instance for assertion failure reporting.
        actual: Generated GNF content to validate.
        expected: Reference GNF content for comparison.
        fromfile: Label for expected content in diff output.
        tofile: Label for actual content in diff output.

    Raises:
        AssertionError: When GNF content differs, includes unified diff.

    """
    if actual != expected:
        expected_lines = expected.splitlines(keepends=True)
        actual_lines = actual.splitlines(keepends=True)

        diff_lines = difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile=fromfile,
            tofile=tofile,
            lineterm="\n",
            n=0,
        )
        diff_text = "".join(diff_lines)

        testcase.fail(
            f"\n=== GNF files differ (unified diff, no context) ===\n{diff_text}"
        )
