from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.type_reader import Types


class TestApplyTypesOnElements(unittest.TestCase):
    def test_lv_cable_no_type_then_apply(self) -> None:
        # Start with a cable that has no cable_type and empty CablePart.type
        cable = CableLV(
            general=CableLV.General(name="C"),
            presentations=[],
            cable_part=CableLV.CablePart(length=1.0, type=""),
        )

        self.assertIsNone(cable.cable_type)
        self.assertEqual(cable.cable_part.type, "")

        # Build a tiny Excel with a single LV Cable type
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            cable_df = pd.DataFrame(
                {
                    "Name": ["XPLE 4x150"],
                    "Shortname": ["XPLE150"],
                    "Unom": [400],
                }
            )
            with pd.ExcelWriter(path) as writer:
                cable_df.to_excel(writer, sheet_name="Cable", index=False)

            types = Types(str(path))

            # Apply by Name (name-only resolution)
            cable.set_cable(types, "XPLE 4x150")

        self.assertIsNotNone(cable.cable_type)
        if cable.cable_type:
            self.assertEqual(cable.cable_type.short_name, "XPLE150")
        self.assertEqual(cable.cable_part.type, "XPLE150")

    def test_lv_fuse_no_type_then_apply(self) -> None:
        # Start with a fuse that has no FuseType object
        fuse = FuseLV(general=FuseLV.General(name="F", fuse_type="16A"))

        self.assertIsNone(fuse.fuse_type)

        # Build a tiny Excel with a single LV Fuse type
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            fuse_df = pd.DataFrame(
                {
                    "Name": ["16A"],
                    "Shortname": ["16A"],
                    "Unom": [230],
                    "Inom": [16.0],
                }
            )
            with pd.ExcelWriter(path) as writer:
                fuse_df.to_excel(writer, sheet_name="Fuse", index=False)

            types = Types(str(path))

            # Apply by name
            fuse.set_fuse_type(types, "16A")

        self.assertIsNotNone(fuse.fuse_type)
        if fuse.fuse_type:
            self.assertEqual(fuse.fuse_type.short_name, "16A")
            self.assertEqual(fuse.fuse_type.unom, 230)
            self.assertEqual(fuse.fuse_type.inom, 16.0)


if __name__ == "__main__":
    unittest.main()
