from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader._excel import normalize_rows, read_sheet


class TestExcelHelpers(unittest.TestCase):
    def test_read_sheet_missing_returns_empty(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            # Create a workbook with a different sheet
            with pd.ExcelWriter(path) as writer:
                pd.DataFrame({"A": [1]}).to_excel(
                    writer, sheet_name="Other", index=False
                )

            rows = read_sheet(str(path), sheet_name="Unknown", skiprows=())
            self.assertEqual(rows, [])

    def test_normalize_rows_rename_and_drop(self) -> None:
        rows = [
            {"Shortname": "S1", "Name": "N1"},
            {"Shortname": None, "Name": None},
        ]
        norm = normalize_rows(rows, rename={"Shortname": "ShortName"})
        self.assertIn("ShortName", norm[0])
        # One all-empty row dropped
        self.assertEqual(len(norm), 1)


if __name__ == "__main__":
    unittest.main()
