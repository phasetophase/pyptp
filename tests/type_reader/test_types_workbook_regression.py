from __future__ import annotations

import unittest
from dataclasses import fields as dataclass_fields
from pathlib import Path
from typing import cast

import pandas as pd

import pyptp.type_reader as tr
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.shared import CableType as LVCableType
from pyptp.elements.lv.shared import FuseType as LVFuseType
from pyptp.type_reader import Types
from pyptp.type_reader._excel import clean_row_dict, read_frame_with_fallback


def _workbook_path() -> Path:
    return Path(tr.__file__).with_name("types.xlsx")


def _pick_first_nonempty_name(frame: pd.DataFrame) -> str | None:
    if "Name" not in frame.columns:
        return None
    series = frame["Name"].dropna()
    for val in series:
        s = str(val).strip()
        if s:
            return s
    return None


def _read_sample_cable_and_fuse() -> tuple[str | None, str | None]:
    path = _workbook_path()
    cable_df = pd.read_excel(path, sheet_name="Cable")
    fuse_df = pd.read_excel(path, sheet_name="Fuse")
    cable_name = _pick_first_nonempty_name(cable_df)
    fuse_name = _pick_first_nonempty_name(fuse_df)
    return cable_name, fuse_name


class TestTypesWorkbookRegression(unittest.TestCase):
    def test_apply_types_from_real_workbook_lv_cable_and_fuse(self) -> None:
        # Ensure workbook exists in repo
        self.assertTrue(
            _workbook_path().exists(), "types.xlsx not found next to type_reader module"
        )

        cable_key, fuse_key = _read_sample_cable_and_fuse()
        self.assertIsNotNone(cable_key, "No cable type found in workbook")
        self.assertIsNotNone(fuse_key, "No fuse type found in workbook")
        if cable_key is None or fuse_key is None:
            self.skipTest("Workbook did not provide sample keys")

        types = Types()

        cable = CableLV(
            general=CableLV.General(name="C"),
            presentations=[],
            cable_part=CableLV.CablePart(length=1.0, type=""),
        )
        self.assertIsNone(cable.cable_type)
        self.assertEqual(cable.cable_part.type, "")

        cable.set_cable(types, cable_key)
        self.assertIsNotNone(cable.cable_type)
        expected_cable = types.get_lv_cable(cable_key)
        self.assertIsNotNone(expected_cable)
        self.assertIs(cable.cable_type, expected_cable)
        if cable.cable_type:
            ct_typed = cast("LVCableType", cable.cable_type)
            self.assertEqual(cable.cable_part.type, ct_typed.short_name)
            self._assert_lv_cable_type_filled(ct_typed)

        # Fuse: starts without type, then apply (use Name-only)
        fuse = FuseLV(general=FuseLV.General(name="F", fuse_type=str(fuse_key)))
        self.assertIsNone(fuse.fuse_type)

        fuse.set_fuse_type(types, str(fuse_key))
        self.assertIsNotNone(fuse.fuse_type)
        expected_fuse = types.get_lv_fuse(str(fuse_key))
        self.assertIsNotNone(expected_fuse)
        self.assertIs(fuse.fuse_type, expected_fuse)
        if fuse.fuse_type:
            ft_typed = cast("LVFuseType", fuse.fuse_type)
            self._assert_lv_fuse_type_filled(ft_typed)

    def test_lv_cable_exact_values_match_excel_row(self) -> None:
        path = _workbook_path()
        frame = read_frame_with_fallback(
            str(path),
            sheet_name="Cable",
            rename={"Shortname": "ShortName", "Tan_delta": "TanDelta"},
        )
        self.assertFalse(frame.empty, "Cable sheet is empty in workbook")

        row = frame.iloc[0]
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        self.assertTrue(name)

        # Load from Types
        types = Types()
        cable_obj_any = types.get_lv_cable(name)
        self.assertIsNotNone(cable_obj_any)
        if cable_obj_any is None:
            self.fail("Types.get_lv_cable returned None")

        cable_typed = cast("LVCableType", cable_obj_any)
        expected_from_row = LVCableType.deserialize(row_dict)

        # Compare every field
        for f in dataclass_fields(LVCableType):
            actual = getattr(cable_typed, f.name)
            expected = getattr(expected_from_row, f.name)
            self.assertEqual(
                actual,
                expected,
                msg=f"Mismatch for CableType.{f.name}: actual={actual!r} expected={expected!r}",
            )

    def test_lv_fuse_exact_values_match_excel_row(self) -> None:
        path = _workbook_path()
        frame = read_frame_with_fallback(
            str(path), sheet_name="Fuse", rename={"Shortname": "ShortName"}
        )
        self.assertFalse(frame.empty, "Fuse sheet is empty in workbook")

        row = frame.iloc[0]
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        self.assertTrue(name)

        types = Types()
        fuse_obj_any = types.get_lv_fuse(name)
        self.assertIsNotNone(fuse_obj_any)
        if fuse_obj_any is None:
            self.fail("Types.get_lv_fuse returned None")

        fuse_typed = cast("LVFuseType", fuse_obj_any)
        expected_from_row = LVFuseType.deserialize(row_dict)

        # Compare every field
        for f in dataclass_fields(LVFuseType):
            actual = getattr(fuse_typed, f.name)
            expected = getattr(expected_from_row, f.name)
            self.assertEqual(
                actual,
                expected,
                msg=f"Mismatch for FuseType.{f.name}: actual={actual!r} expected={expected!r}",
            )

    def test_lv_cable_all_names_match_excel_rows(self) -> None:
        # Verify ALL Name rows match exactly between workbook and Types (for rows that deserialize)
        path = _workbook_path()
        frame = read_frame_with_fallback(
            str(path),
            sheet_name="Cable",
            rename={"Shortname": "ShortName", "Tan_delta": "TanDelta"},
        )
        self.assertFalse(frame.empty, "Cable sheet is empty in workbook")

        types = Types()
        # Build expected objects using the same deserializer, skipping rows that would be skipped by loader
        expected_by_name: dict[str, LVCableType] = {}
        for _, row in frame.iterrows():
            row_dict = clean_row_dict(row)
            name = str(row_dict.get("Name", "")).strip()
            if not name:
                continue
            try:
                obj = LVCableType.deserialize(row_dict)
            except Exception:
                continue
            expected_by_name[name] = obj

        self.assertGreater(len(expected_by_name), 0)

        # Compare Types output with expected for every Name
        for name, expected_from_row in expected_by_name.items():
            obj_any = types.get_lv_cable(name)
            self.assertIsNotNone(
                obj_any, msg=f"Types did not return cable for Name '{name}'"
            )
            cable_typed = cast("LVCableType", obj_any)
            for f in dataclass_fields(LVCableType):
                actual = getattr(cable_typed, f.name)
                expected = getattr(expected_from_row, f.name)
                self.assertEqual(
                    actual,
                    expected,
                    msg=f"Mismatch for CableType.{f.name} on Name '{name}': actual={actual!r} expected={expected!r}",
                )

    def test_lv_fuse_all_names_match_excel_rows(self) -> None:
        # Verify ALL Name rows match exactly between workbook and Types (for rows that deserialize)
        path = _workbook_path()
        frame = read_frame_with_fallback(
            str(path), sheet_name="Fuse", rename={"Shortname": "ShortName"}
        )
        self.assertFalse(frame.empty, "Fuse sheet is empty in workbook")

        types = Types()
        expected_by_name: dict[str, LVFuseType] = {}
        for _, row in frame.iterrows():
            row_dict = clean_row_dict(row)
            name = str(row_dict.get("Name", "")).strip()
            if not name:
                continue
            try:
                obj = LVFuseType.deserialize(row_dict)
            except Exception:
                continue
            expected_by_name[name] = obj

        self.assertGreater(len(expected_by_name), 0)

        for name, expected_from_row in expected_by_name.items():
            obj_any = types.get_lv_fuse(name)
            self.assertIsNotNone(
                obj_any, msg=f"Types did not return fuse for Name '{name}'"
            )
            fuse_typed = cast("LVFuseType", obj_any)
            for f in dataclass_fields(LVFuseType):
                actual = getattr(fuse_typed, f.name)
                expected = getattr(expected_from_row, f.name)
                self.assertEqual(
                    actual,
                    expected,
                    msg=f"Mismatch for FuseType.{f.name} on Name '{name}': actual={actual!r} expected={expected!r}",
                )

    def _assert_lv_cable_type_filled(self, ct) -> None:
        self.assertIsInstance(ct, LVCableType)
        self.assertIsInstance(ct.short_name, str)
        self.assertTrue(ct.short_name)

        for f in dataclass_fields(ct):
            if f.name == "short_name":
                continue
            value = getattr(ct, f.name)
            self.assertIsNotNone(value, msg=f"CableType.{f.name} is None")
            self.assertIsInstance(
                value, (int, float), msg=f"CableType.{f.name} not numeric: {value!r}"
            )

    def _assert_lv_fuse_type_filled(self, ft) -> None:
        self.assertIsInstance(ft, LVFuseType)
        self.assertIsInstance(ft.short_name, str)
        self.assertTrue(ft.short_name)
        self.assertIsInstance(ft.unom, (int, float))
        self.assertIsInstance(ft.inom, (int, float))
        # I/T lists must exist, be length 16, and numeric
        self.assertIsNotNone(ft.I)
        self.assertIsNotNone(ft.T)
        self.assertEqual(len(ft.I), 16)
        self.assertEqual(len(ft.T), 16)
        self.assertTrue(
            all(isinstance(x, (int, float)) for x in ft.I),
            msg=f"Non-numeric in I: {ft.I!r}",
        )
        self.assertTrue(
            all(isinstance(x, (int, float)) for x in ft.T),
            msg=f"Non-numeric in T: {ft.T!r}",
        )


if __name__ == "__main__":
    unittest.main()
