from __future__ import annotations

import importlib
import unittest
from types import ModuleType
from unittest.mock import patch

from pyptp.validator import Validator
from pyptp.validator.registry import discover_validators


class TestRegistry(unittest.TestCase):
    def test_discovery_finds_concrete_validators(self) -> None:
        """Registry should return real subclasses while omitting the abstract base."""
        found_validators = discover_validators()
        self.assertTrue(
            any(
                issubclass(validator_class, Validator)
                for validator_class in found_validators
            )
        )
        self.assertFalse(
            any(validator_class is Validator for validator_class in found_validators)
        )

    def test_discovery_continues_on_import_error(self) -> None:
        """Import errors in optional modules must be logged but not break discovery."""
        original_import_module = importlib.import_module

        def fake_import(module_name: str, package: str | None = None) -> ModuleType:
            if module_name.startswith("pyptp.validator.shared.bad_module"):
                raise ImportError("boom")
            return original_import_module(module_name, package=package)

        with (
            patch(
                "pyptp.validator.registry.pkgutil.walk_packages"
            ) as walk_packages_mock,
            patch(
                "pyptp.validator.registry.importlib.import_module",
                side_effect=fake_import,
            ),
        ):
            walk_packages_mock.return_value = [
                (None, "pyptp.validator.shared.bad_module", False)
            ]
            discovered = discover_validators()
            self.assertIsInstance(discovered, list)


if __name__ == "__main__":
    unittest.main()
