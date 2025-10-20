from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.type_reader._aliases import load_alias_map


class TestAliases(unittest.TestCase):
    def test_load_alias_map(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            cable_alias = pd.DataFrame(
                {
                    "Alias": ["C1", ""],
                    "Name": ["Cable One", ""],
                }
            ).set_index("Alias")
            fuse_alias = pd.DataFrame(
                {
                    "Alias": ["F1"],
                    "Name": ["Fuse One"],
                }
            ).set_index("Alias")
            with pd.ExcelWriter(path) as writer:
                cable_alias.to_excel(writer, sheet_name="Cable alias")
                fuse_alias.to_excel(writer, sheet_name="Fuse alias")

            cmap = load_alias_map(str(path), "Cable alias")
            fmap = load_alias_map(str(path), "Fuse alias")
            self.assertEqual(cmap.get("C1"), "Cable One")
            self.assertEqual(fmap.get("F1"), "Fuse One")


if __name__ == "__main__":
    unittest.main()
