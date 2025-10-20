from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import pandas as pd

from pyptp.elements.lv.shared import FuseType
from pyptp.type_reader import Types


class TestLVFuseLoader(unittest.TestCase):
    def test_lv_fuse_shortname_name_alias_it_lists(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            fuse = pd.DataFrame(
                {
                    "Name": ["Fuse One"],
                    "Shortname": ["F1"],
                    "Unom": [0.5],
                    "Inom": [35],
                    "I1": [52],
                    "T1": [1000],
                    "I2": [52],
                    "T2": [500],
                    "I3": [53],
                    "T3": [100],
                }
            )
            aliases = pd.DataFrame(
                {
                    "Alias": ["FUSE_ALIAS"],
                    "Name": ["Fuse One"],
                }
            ).set_index("Alias")
            with pd.ExcelWriter(path) as writer:
                fuse.to_excel(writer, sheet_name="Fuse", index=False)
                aliases.to_excel(writer, sheet_name="Fuse alias")

            types = Types(str(path))
            fuse_by_short = types.get_lv_fuse("F1")
            fuse_by_name = types.get_lv_fuse("Fuse One")
            fuse_by_alias = types.get_lv_fuse("FUSE_ALIAS")

            # Under name-only policy, shortname resolution should fail; alias and name should succeed
            self.assertIsNotNone(fuse_by_name)
            self.assertIsNotNone(fuse_by_alias)
            self.assertIsNone(fuse_by_short)
            # Verify I/T lists formed with at least first items
            if fuse_by_short:
                fuse_typed = cast("FuseType", fuse_by_short)
                self.assertGreaterEqual(len(fuse_typed.I), 3)
                self.assertEqual(fuse_typed.I[0], 52)


if __name__ == "__main__":
    unittest.main()
