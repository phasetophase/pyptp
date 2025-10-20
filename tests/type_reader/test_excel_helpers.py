from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader._excel import normalize_frame, read_sheet


class TestExcelHelpers(unittest.TestCase):
    def test_read_sheet_missing_returns_empty(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            # Create a workbook with a different sheet
            with pd.ExcelWriter(path) as writer:
                pd.DataFrame({"A": [1]}).to_excel(
                    writer, sheet_name="Other", index=False
                )

            df = read_sheet(
                str(path), sheet_name="Unknown", index_col=None, skiprows=()
            )
            self.assertTrue(df.empty)

    def test_normalize_frame_rename_and_drop(self) -> None:
        frame = pd.DataFrame(
            {
                "Shortname": ["S1", None],
                "Name": ["N1", None],
            }
        )
        norm = normalize_frame(frame, rename={"Shortname": "ShortName"})
        self.assertIn("ShortName", norm.columns)
        # One all-empty row dropped
        self.assertEqual(len(norm), 1)


if __name__ == "__main__":
    unittest.main()
