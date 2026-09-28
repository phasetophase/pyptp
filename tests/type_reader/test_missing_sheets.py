from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import MissingSheetError, Types


class TestMissingSheets(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self.path = Path(self._tempdir.name) / "wb.xlsx"
        with pd.ExcelWriter(self.path) as writer:
            pd.DataFrame({"A": [1]}).to_excel(writer, sheet_name="Other", index=False)

    def test_every_lookup_names_the_sheet_it_misses(self) -> None:
        types = Types(str(self.path))
        for lookup, sheet in (
            (types.get_lv_cable, "Cable"),
            (types.get_mv_cable, "Cable"),
            (types.get_lv_fuse, "Fuse"),
            (types.get_mv_fuse, "Fuse"),
            (types.get_lv_transformer, "Trafo"),
            (types.get_mv_transformer, "Trafo"),
            (types.get_lv_gm_type, "GM"),
        ):
            with self.subTest(sheet=sheet):
                with self.assertRaises(MissingSheetError) as ctx:
                    lookup("X")
                self.assertIn(repr(sheet), str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
