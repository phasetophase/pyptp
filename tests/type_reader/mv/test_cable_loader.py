from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import Types, UnknownTypeError


class TestMVCableLoader(unittest.TestCase):
    def test_mv_cable_info_default_and_resolution(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            cable = pd.DataFrame(
                {
                    "Name": ["MV Cable"],
                    "Shortname": ["MC1"],
                    "R": [0.1],
                    "X": [0.2],
                }
            )
            aliases = pd.DataFrame(
                {
                    "Alias": ["MV_CABLE_ALIAS"],
                    "Name": ["MV Cable"],
                }
            ).set_index("Alias")
            with pd.ExcelWriter(path) as writer:
                cable.to_excel(writer, sheet_name="Cable", index=False)
                aliases.to_excel(writer, sheet_name="Cable alias")

            types = Types(str(path))
            # ShortName should not resolve under name-only policy
            with self.assertRaises(UnknownTypeError):
                types.get_mv_cable("MC1")
            # Name should resolve and set info to Name
            mv_cable_by_name = types.get_mv_cable("MV Cable")
            self.assertEqual(mv_cable_by_name.info, "MV Cable")
            by_alias = types.get_mv_cable("MV_CABLE_ALIAS")
            self.assertEqual(by_alias, mv_cable_by_name)


if __name__ == "__main__":
    unittest.main()
