from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import Types, UnknownTypeError


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
            fuse_by_name = types.get_lv_fuse("Fuse One")
            fuse_by_alias = types.get_lv_fuse("FUSE_ALIAS")

            self.assertEqual(fuse_by_alias, fuse_by_name)
            # Under name-only policy, a ShortName does not resolve
            with self.assertRaises(UnknownTypeError):
                types.get_lv_fuse("F1")

            # the I1..I3 columns become one list
            self.assertEqual((fuse_by_name.I or [])[:3], [52, 52, 53])


if __name__ == "__main__":
    unittest.main()
