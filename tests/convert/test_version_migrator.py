"""Tests for the native migrator wrapper: conversion, validation and error reporting."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pyptp import NetworkLV, NetworkMV
from pyptp.convert.version_migrator import (
    ERR_INVALID_VERSION,
    ERR_LOAD_FAILURE,
    ERR_NETWORK_INVALID,
    ERR_SUCCESS,
    NativeResult,
    convert_file,
    migrate_and_read,
    save_as,
    validate_file,
)
from pyptp.elements.enums import VnfVersion
from pyptp.elements.mv.measure_field import MeasureFieldMV


def _network_with_unassigned_measure_field() -> NetworkMV:
    """Network with a measure field without an in-object, which the loader rejects."""
    network = NetworkMV()
    MeasureFieldMV(general=MeasureFieldMV.General(), presentations=[]).register(network)
    return network


class NativeLibraryTestCase(unittest.TestCase):
    """Shared temporary directory and network files for the migrator tests."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.temp_dir = Path(self._temp.name)

        self.valid_vnf = self.temp_dir / "valid.vnf"
        NetworkMV().save(self.valid_vnf)

        self.invalid_vnf = self.temp_dir / "invalid.vnf"
        _network_with_unassigned_measure_field().save(
            self.invalid_vnf, native_check=False
        )


class TestValidateFile(NativeLibraryTestCase):
    def test_valid_vnf_is_accepted(self) -> None:
        result = validate_file(self.valid_vnf)

        self.assertTrue(result.ok)
        self.assertEqual(result.code, ERR_SUCCESS)
        self.assertEqual(result.errors, [])

    def test_valid_gnf_is_accepted(self) -> None:
        gnf = self.temp_dir / "valid.gnf"
        NetworkLV().save(gnf)

        result = validate_file(gnf)

        self.assertTrue(result.ok, result.describe())

    def test_rejected_content_reports_loader_error(self) -> None:
        result = validate_file(self.invalid_vnf)

        self.assertEqual(result.code, ERR_NETWORK_INVALID)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("Meetveld", result.errors[0])
        self.assertIn("in-object niet toegekend", result.errors[0])

    def test_missing_file_is_a_load_failure(self) -> None:
        result = validate_file(self.temp_dir / "missing.vnf")

        self.assertEqual(result.code, ERR_LOAD_FAILURE)
        self.assertTrue(result.errors)

    def test_unknown_extension_is_a_load_failure(self) -> None:
        result = validate_file(self.temp_dir / "network.txt")

        self.assertEqual(result.code, ERR_LOAD_FAILURE)
        self.assertIn("not a .gnf or .vnf file", result.errors[0])

    def test_describe_lists_every_message(self) -> None:
        result = NativeResult(
            code=ERR_NETWORK_INVALID, errors=["first", "second"], warnings=["careful"]
        )

        self.assertEqual(
            result.describe(),
            "The network file contains errors.\n  error: first\n  error: second\n  warning: careful",
        )


class TestConvertFile(NativeLibraryTestCase):
    def test_valid_network_converts_to_older_version(self) -> None:
        result = convert_file(self.valid_vnf, self.temp_dir, "older.vnf", "V9.11")

        self.assertTrue(result.ok, result.describe())
        self.assertTrue(
            (self.temp_dir / "older.vnf")
            .read_text(encoding="utf-8")
            .startswith("V9.11")
        )

    def test_rejected_content_leaves_no_output(self) -> None:
        result = convert_file(self.invalid_vnf, self.temp_dir, "older.vnf", "V9.11")

        self.assertEqual(result.code, ERR_NETWORK_INVALID)
        self.assertIn("in-object niet toegekend", result.errors[0])
        self.assertFalse((self.temp_dir / "older.vnf").exists())

    def test_invalid_version_string(self) -> None:
        result = convert_file(self.valid_vnf, self.temp_dir, "older.vnf", "V1.0")

        self.assertEqual(result.code, ERR_INVALID_VERSION)
        self.assertIn("V1.0", result.errors[0])

    def test_save_as_returns_text_with_loader_errors(self) -> None:
        self.assertEqual(
            save_as(str(self.valid_vnf), str(self.temp_dir), "ok.vnf", "V9.11"),
            "Conversion successful",
        )

        message = save_as(str(self.invalid_vnf), str(self.temp_dir), "bad.vnf", "V9.11")

        self.assertNotIn("successful", message.lower())
        self.assertIn("in-object niet toegekend", message)


class TestMigrateAndRead(NativeLibraryTestCase):
    def test_older_file_is_upgraded(self) -> None:
        older = self.temp_dir / "older.vnf"
        self.assertTrue(
            convert_file(self.valid_vnf, self.temp_dir, older.name, "V9.11").ok
        )

        content = migrate_and_read(older, version="V9.12")

        self.assertTrue(content.startswith("V9.12"))

    def test_rejected_content_raises_with_loader_errors_and_no_retry(self) -> None:
        with (
            patch("pyptp.convert.version_migrator.time.sleep") as sleep,
            self.assertRaises(RuntimeError) as ctx,
        ):
            migrate_and_read(self.invalid_vnf, version="V9.12")

        self.assertIn("in-object niet toegekend", str(ctx.exception))
        self.assertIn("invalid.vnf", str(ctx.exception))
        sleep.assert_not_called()


class TestExportErrors(NativeLibraryTestCase):
    def test_saving_older_version_reports_loader_errors(self) -> None:
        network = _network_with_unassigned_measure_field()

        with self.assertRaises(RuntimeError) as ctx:
            network.save(self.temp_dir / "older.vnf", VnfVersion.V9_11)

        message = str(ctx.exception)
        self.assertIn("Failed to convert to V9.11", message)
        self.assertIn("in-object niet toegekend", message)

    def test_saving_latest_version_does_not_use_migrator(self) -> None:
        path = self.temp_dir / "latest.vnf"

        with patch("pyptp.IO.exporters.vnf_exporter.convert_file") as convert:
            NetworkMV().save(path)

        convert.assert_not_called()
        self.assertTrue(path.exists())

    def test_saving_latest_version_runs_native_check(self) -> None:
        network = _network_with_unassigned_measure_field()
        path = self.temp_dir / "latest.vnf"

        with self.assertRaises(RuntimeError) as ctx:
            network.save(path)

        self.assertIn("Failed to save as V9.12", str(ctx.exception))
        self.assertIn("in-object niet toegekend", str(ctx.exception))
        self.assertFalse(path.exists())

    def test_saving_with_native_check_off_writes_file(self) -> None:
        network = _network_with_unassigned_measure_field()
        path = self.temp_dir / "latest.vnf"

        network.save(path, native_check=False)

        self.assertTrue(path.read_text(encoding="utf-8").startswith("V9.12"))

    def test_saving_latest_gnf_runs_native_check(self) -> None:
        path = self.temp_dir / "latest.gnf"

        with patch(
            "pyptp.IO.exporters.gnf_exporter.validate_file", wraps=validate_file
        ) as check:
            NetworkLV().save(path)

        check.assert_called_once()
        self.assertTrue(path.exists())


class TestImportErrors(NativeLibraryTestCase):
    def test_loading_latest_version_runs_native_check(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            NetworkMV.from_file(self.invalid_vnf)

        self.assertIn("Failed to load 'invalid.vnf'", str(ctx.exception))
        self.assertIn("in-object niet toegekend", str(ctx.exception))

    def test_loading_with_native_check_off_parses_file(self) -> None:
        network = NetworkMV.from_file(self.invalid_vnf, native_check=False)

        self.assertEqual(len(network.measure_fields), 1)

    def test_loading_valid_latest_version(self) -> None:
        network = NetworkMV.from_file(self.valid_vnf)

        self.assertEqual(len(network.measure_fields), 0)

    def test_loading_latest_gnf_runs_native_check(self) -> None:
        gnf = self.temp_dir / "valid.gnf"
        NetworkLV().save(gnf)

        with patch(
            "pyptp.IO.importers.gnf_importer.validate_file", wraps=validate_file
        ) as check:
            NetworkLV.from_file(gnf)

        check.assert_called_once()


if __name__ == "__main__":
    unittest.main()
