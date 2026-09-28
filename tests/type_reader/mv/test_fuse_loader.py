from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import Types, UnknownTypeError


class TestMVFuseLoader(unittest.TestCase):
    def test_mv_fuse_resolution(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            fuse = pd.DataFrame(
                {
                    "Name": ["MV Fuse"],
                    "Shortname": ["MF1"],
                    "Unom": [10],
                    "Inom": [200],
                    "I1": [100],
                    "T1": [1],
                }
            )
            aliases = pd.DataFrame(
                {
                    "Alias": ["MV_FUSE_ALIAS"],
                    "Name": ["MV Fuse"],
                }
            ).set_index("Alias")
            with pd.ExcelWriter(path) as writer:
                fuse.to_excel(writer, sheet_name="Fuse", index=False)
                aliases.to_excel(writer, sheet_name="Fuse alias")

            types = Types(str(path))
            # ShortName should not resolve under name-only policy
            with self.assertRaises(UnknownTypeError):
                types.get_mv_fuse("MF1")
            fuse = types.get_mv_fuse("MV Fuse")
            self.assertEqual(fuse.short_name, "MF1")
            by_alias = types.get_mv_fuse("MV_FUSE_ALIAS")
            self.assertEqual(by_alias, fuse)


if __name__ == "__main__":
    unittest.main()
