# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Docstring wording rules that apply to the whole package."""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent / "pyptp"


def parse_package() -> list[tuple[Path, ast.Module]]:
    modules = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules.append((path, tree))
    return modules


def field_docstrings(tree: ast.Module) -> list[tuple[int, str]]:
    """Return line and text of each string that directly follows an annotated class attribute."""
    docstrings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for previous, statement in zip(node.body, node.body[1:], strict=False):
            if not isinstance(previous, ast.AnnAssign):
                continue
            if not isinstance(statement, ast.Expr) or not isinstance(
                statement.value, ast.Constant
            ):
                continue
            text = statement.value.value
            if isinstance(text, str):
                docstrings.append((statement.lineno, text))
    return docstrings


class TestDocstrings(unittest.TestCase):
    def test_no_semicolons(self) -> None:
        offenders = []
        for path, tree in parse_package():
            for node in ast.walk(tree):
                if not isinstance(
                    node,
                    (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    continue
                docstring = ast.get_docstring(node, clean=False)
                if docstring and re.search(r";\s", docstring):
                    line = getattr(node, "lineno", 1)
                    offenders.append(f"{path.relative_to(PACKAGE_DIR)}:{line}")
            for line, docstring in field_docstrings(tree):
                if re.search(r";\s", docstring):
                    offenders.append(f"{path.relative_to(PACKAGE_DIR)}:{line}")

        self.assertEqual(offenders, [])

    def test_field_docstrings_do_not_name_the_application(self) -> None:
        offenders = []
        for path, tree in parse_package():
            for line, docstring in field_docstrings(tree):
                if re.search(
                    r"\b(Vision|Gaia|dialog|caption|checkbox|button)s?\b",
                    docstring,
                    re.IGNORECASE,
                ):
                    offenders.append(f"{path.relative_to(PACKAGE_DIR)}:{line}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
