from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from pyptp.elements.lv.transformer import TransformerLV
from pyptp.type_reader import Types, UnknownTypeError

TRAFO_SHEET = pd.DataFrame(
    {
        "Name": ["10250/400 V   50 kVA"],
        "Shortname": ["50 kVA"],
        "Unom1": [10.25],
        "Unom2": [0.4],
        "Snom": [0.05],
        "Uk": [4.0],
        "Pk": [0.9],
        "Pnul": [0.12],
        "Inul": [0.0],
        "R0": [0.0576],
        "Z0": [0.1143],
        "Side Z0": [0],
        "Ik2s": [1.8],
        "s1": ["D"],
        "s2": ["yn"],
        "Clock": [5],
        "Tapside": [1],
        "Tapsize": [0.25],
        "Tapmin": [-2],
        "Tapnom": [0],
        "Tapmax": [2],
    }
)


def _write_workbook(path: Path, *, with_alias: bool = False) -> None:
    with pd.ExcelWriter(path) as writer:
        TRAFO_SHEET.to_excel(writer, sheet_name="Trafo", index=False)
        if with_alias:
            pd.DataFrame(
                {"Alias": ["50kVA"], "Name": ["10250/400 V   50 kVA"]}
            ).set_index("Alias").to_excel(writer, sheet_name="Trafo alias")


class TestTransformerLookup(unittest.TestCase):
    def test_lv_transformer_renamed_headers(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            transformer = Types(str(path)).get_lv_transformer("10250/400 V   50 kVA")

            self.assertEqual(transformer.short_name, "50 kVA")
            self.assertEqual(transformer.snom, 0.05)
            self.assertEqual(transformer.Po, 0.12)
            self.assertEqual(transformer.Io, 0.0)
            self.assertEqual(transformer.winding_connection1, "D")
            self.assertEqual(transformer.winding_connection2, "yn")
            self.assertEqual(transformer.clock_number, 5)
            self.assertEqual(transformer.tap_min, -2)

    def test_mv_transformer_reads_side_z0(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            transformer = Types(str(path)).get_mv_transformer("10250/400 V   50 kVA")

            self.assertEqual(transformer.short_name, "50 kVA")
            self.assertEqual(transformer.po, 0.12)
            self.assertEqual(transformer.side_z0, 0)
            self.assertEqual(transformer.winding_connection2, "yn")

    def test_alias_resolves(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path, with_alias=True)

            types = Types(str(path))

            by_alias = types.get_lv_transformer("50kVA")
            by_name = types.get_lv_transformer("10250/400 V   50 kVA")

            self.assertEqual(by_alias, by_name)

    def test_an_alias_resolves_to_the_type_name(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path, with_alias=True)

            name = Types(str(path)).type_name("lv_transformer", "50kVA")

            self.assertEqual(name, "10250/400 V   50 kVA")

    def test_unknown_name_raises_with_a_suggestion(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            with self.assertRaises(UnknownTypeError) as ctx:
                Types(str(path)).get_lv_transformer("10250/400 V   50 kVa")

            message = str(ctx.exception)
            self.assertIn("10250/400 V   50 kVa", message)
            self.assertIn("10250/400 V   50 kVA", message)
            self.assertIn(str(path), message)

    def test_a_name_used_twice_warns_and_the_last_row_wins(self) -> None:
        first = TRAFO_SHEET.copy()
        second = TRAFO_SHEET.copy()
        second["Shortname"] = ["50 kVA tweede"]
        sheet = pd.concat([first, second], ignore_index=True)
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            with pd.ExcelWriter(path) as writer:
                sheet.to_excel(writer, sheet_name="Trafo", index=False)

            with self.assertLogs("pyptp", level="WARNING") as logs:
                transformer = Types(str(path)).get_lv_transformer(
                    "10250/400 V   50 kVA"
                )

            self.assertEqual(transformer.short_name, "50 kVA tweede")
            self.assertEqual(len(logs.records), 1)
            self.assertIn("10250/400 V   50 kVA", logs.output[0])

    def test_short_name_does_not_resolve(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            with self.assertRaises(UnknownTypeError):
                Types(str(path)).get_lv_transformer("50 kVA")

    def test_a_lookup_returns_a_new_object(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            types = Types(str(path))
            first = types.get_lv_transformer("10250/400 V   50 kVA")
            first.snom = 99.0

            second = types.get_lv_transformer("10250/400 V   50 kVA")

            self.assertEqual(second.snom, 0.05)

    def test_workbook_transformer_matches_its_row(self) -> None:
        transformer = Types().get_lv_transformer("10250/400 V  630 kVA")

        self.assertEqual(transformer.short_name, "630 kVA")
        self.assertEqual(transformer.snom, 0.63)
        self.assertEqual(transformer.unom1, 10.25)
        self.assertEqual(transformer.unom2, 0.4)
        self.assertEqual(transformer.Uk, 4)
        self.assertEqual(transformer.Pk, 5.4)
        self.assertEqual(transformer.Po, 0.75)
        self.assertEqual(transformer.R0, 0.0022)
        self.assertEqual(transformer.Z0, 0.0099)
        self.assertEqual(transformer.ik2s, 22.7)
        self.assertEqual(transformer.tap_min, -2)
        self.assertEqual(transformer.tap_max, 2)
        self.assertEqual(transformer.ki, 11)
        self.assertEqual(transformer.tau, 0.3)


class TestStrictLookup(unittest.TestCase):
    def test_column_renames_accepts_the_transformer_keys(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            types = Types(
                str(path), column_renames={"lv_transformer": {"Snom": "Unom1"}}
            )

            self.assertEqual(
                types.get_lv_transformer("10250/400 V   50 kVA").unom1, 0.05
            )

    def test_unknown_rename_key_still_raises(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            with self.assertRaises(ValueError):
                Types(str(path), column_renames={"lv_trafo": {}})

    def test_a_sheet_is_read_once(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)
            types = Types(str(path))
            types.get_lv_transformer("10250/400 V   50 kVA")

            changed = TRAFO_SHEET.copy()
            changed["Shortname"] = ["50 kVA gewijzigd"]
            with pd.ExcelWriter(path) as writer:
                changed.to_excel(writer, sheet_name="Trafo", index=False)
            transformer = types.get_lv_transformer("10250/400 V   50 kVA")

            self.assertEqual(transformer.short_name, "50 kVA")

    def test_a_missing_workbook_raises_at_construction(self) -> None:
        with self.assertRaises(FileNotFoundError):
            Types("does-not-exist.xlsx")

    def test_an_unreadable_row_names_the_type_and_the_workbook(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_workbook(path)

            types = Types(str(path))
            with (
                patch.object(
                    TransformerLV.TransformerType,
                    "deserialize",
                    side_effect=ValueError("boom"),
                ),
                self.assertRaises(ValueError) as ctx,
            ):
                types.get_lv_transformer("10250/400 V   50 kVA")

            message = str(ctx.exception)
            self.assertIn("10250/400 V   50 kVA", message)
            self.assertIn(str(path), message)


if __name__ == "__main__":
    unittest.main()
