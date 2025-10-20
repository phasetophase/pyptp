from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader import Types


class TestLVCableLoader(unittest.TestCase):
    def test_lv_cable_shortname_name_alias(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            # Shuffle columns intentionally
            cable = pd.DataFrame(
                {
                    "Name": ["Cable One"],
                    "R": [0.1],
                    "Shortname": ["C1"],
                    "X": [0.2],
                }
            )
            aliases = pd.DataFrame(
                {
                    "Alias": ["CABLE_ALIAS"],
                    "Name": ["Cable One"],
                }
            ).set_index("Alias")
            with pd.ExcelWriter(path) as writer:
                cable.to_excel(writer, sheet_name="Cable", index=False)
                aliases.to_excel(writer, sheet_name="Cable alias")

            types = Types(str(path))
            cable_by_short = types.get_lv_cable("C1")
            cable_by_name = types.get_lv_cable("Cable One")
            cable_by_alias = types.get_lv_cable("CABLE_ALIAS")

            # Name should resolve, alias should resolve, shortname should NOT (name-only policy)
            self.assertIsNotNone(cable_by_name)
            self.assertIsNotNone(cable_by_alias)
            self.assertIsNone(cable_by_short)


if __name__ == "__main__":
    unittest.main()
