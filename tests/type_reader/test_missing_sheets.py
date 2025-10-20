from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import Types


class TestMissingSheets(unittest.TestCase):
    def test_construct_with_missing_sheets(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            # Create workbook without Cable/Fuse
            with pd.ExcelWriter(path) as writer:
                pd.DataFrame({"A": [1]}).to_excel(
                    writer, sheet_name="Other", index=False
                )

            types = Types(str(path))
            # Lookups return None gracefully
            self.assertIsNone(types.get_lv_cable("X"))
            self.assertIsNone(types.get_lv_fuse("X"))
            self.assertIsNone(types.get_mv_cable("X"))
            self.assertIsNone(types.get_mv_fuse("X"))


if __name__ == "__main__":
    unittest.main()
