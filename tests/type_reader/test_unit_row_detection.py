from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader._excel import read_type_sheet


def _write_sheet(path: Path, frame: pd.DataFrame, sheet_name: str = "Cable") -> None:
    with pd.ExcelWriter(path) as writer:
        frame.to_excel(writer, sheet_name=sheet_name, index=False)


class TestUnitRowDetection(unittest.TestCase):
    def test_no_unit_row_keeps_first_data_row(self) -> None:
        # Regression: skiprows=(1,) silently dropped the first data row of
        # workbooks without a unit row.
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": ["Cable One", "Cable Two"],
                        "R": [0.1, 0.2],
                    }
                ),
            )

            rows = read_type_sheet(str(path), "Cable")
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["Name"], "Cable One")

    def test_unit_row_is_dropped(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": [None, "Cable One", "Cable Two"],
                        "R": ["Ohm/km", 0.1, 0.2],
                    }
                ),
            )

            rows = read_type_sheet(str(path), "Cable")
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["Name"], "Cable One")

    def test_header_only_sheet_returns_empty(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(path, pd.DataFrame({"Name": [], "R": []}))

            self.assertEqual(read_type_sheet(str(path), "Cable"), [])

    def test_missing_sheet_returns_empty(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path, pd.DataFrame({"Name": ["Cable One"]}), sheet_name="Other"
            )

            self.assertEqual(read_type_sheet(str(path), "Cable"), [])

    def test_no_name_column_keeps_all_rows(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path,
                pd.DataFrame(
                    {
                        "Alias": [None, "A1"],
                        "Target": ["unit-ish", "T1"],
                    }
                ),
            )

            rows = read_type_sheet(str(path), "Cable")
            self.assertEqual(len(rows), 2)

    def test_shortname_only_sheet_drops_unit_row(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path,
                pd.DataFrame(
                    {
                        "ShortName": [None, "C1"],
                        "R": ["Ohm/km", 0.1],
                    }
                ),
            )

            rows = read_type_sheet(str(path), "Cable")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["ShortName"], "C1")

    def test_rename_onto_name_participates_in_detection(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_sheet(
                path,
                pd.DataFrame(
                    {
                        "Naam": [None, "Cable One"],
                        "R": ["Ohm/km", 0.1],
                    }
                ),
            )

            rows = read_type_sheet(str(path), "Cable", rename={"Naam": "Name"})
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["Name"], "Cable One")


if __name__ == "__main__":
    unittest.main()
