from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import pandas as pd

from pyptp.elements.lv.shared import CableType as LVCableType
from pyptp.elements.mv.shared import CableType as MVCableType
from pyptp.type_reader import Types


def _write_cable_sheet(path: Path, frame: pd.DataFrame) -> None:
    with pd.ExcelWriter(path) as writer:
        frame.to_excel(writer, sheet_name="Cable", index=False)


class TestColumnRenames(unittest.TestCase):
    def test_lv_cable_custom_rename_applied(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": ["Cable One"],
                        "Shortname": ["C1"],
                        "R_ohm": [0.125],
                    }
                ),
            )

            types = Types(str(path), column_renames={"lv_cable": {"R_ohm": "R_c"}})
            cable = types.get_lv_cable("Cable One")
            self.assertIsNotNone(cable)
            cable_typed = cast("LVCableType", cable)
            self.assertEqual(cable_typed.R_c, 0.125)
            # A custom rename does not disturb case-insensitive matching
            self.assertEqual(cable_typed.short_name, "C1")

    def test_renames_are_isolated_per_loader(self) -> None:
        # LV and MV cables come from the same 'Cable' sheet, so a rename keyed
        # for one loader must not leak into the other.
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": ["Cable One"],
                        "Shortname": ["C1"],
                        "R_ohm": [0.125],
                    }
                ),
            )

            types = Types(str(path), column_renames={"mv_cable": {"R_ohm": "R"}})

            mv_cable = cast("MVCableType", types.get_mv_cable("Cable One"))
            self.assertEqual(mv_cable.r, 0.125)

            lv_cable = cast("LVCableType", types.get_lv_cable("Cable One"))
            self.assertEqual(lv_cable.R_c, 0)

    def test_unknown_key_raises(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(path, pd.DataFrame({"Name": ["Cable One"]}))

            with self.assertRaises(ValueError) as ctx:
                Types(str(path), column_renames={"lv_cabel": {"R_ohm": "R_c"}})
            self.assertIn("lv_cabel", str(ctx.exception))

    def test_headers_match_ignoring_case(self) -> None:
        # Regression: the Cable sheet writes 'R_C' and 'Shortname' where the
        # dataclasses read 'R_c' and 'ShortName', so every LV impedance
        # silently stayed 0.
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": ["Cable One"],
                        "SHORTNAME": ["C1"],
                        "R_C": [0.69],
                        "x_c": [0.83],
                    }
                ),
            )

            lv_cable = cast("LVCableType", Types(str(path)).get_lv_cable("Cable One"))
            self.assertEqual(lv_cable.short_name, "C1")
            self.assertEqual(lv_cable.R_c, 0.69)
            self.assertEqual(lv_cable.X_c, 0.83)

    def test_mv_cable_default_renames(self) -> None:
        # Headers differing from the VNF property name by more than case.
        # Vision reads VOP into Loopsnelheid, which it serializes as
        # PulseVelocity (leestypen.pas, loadV9xx.pas).
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame(
                    {"Name": ["Cable One"], "Tan_delta": [0.07], "VoP": [150]}
                ),
            )

            mv_cable = cast("MVCableType", Types(str(path)).get_mv_cable("Cable One"))
            self.assertEqual(mv_cable.tan_delta, 0.07)
            self.assertEqual(mv_cable.pulse_velocity, 150)

    def test_lv_cable_t_suffix_default_renames(self) -> None:
        # Vision accepts both a _T and a _O suffix for these columns; the GNF
        # property name uses _o (leestypen.pas).
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame(
                    {
                        "Name": ["Cable One"],
                        "R_CC_T": [0.0492],
                        "X_CH_T": [0.71],
                        "R_HH_T": [0.33],
                    }
                ),
            )

            lv_cable = cast("LVCableType", Types(str(path)).get_lv_cable("Cable One"))
            self.assertEqual(lv_cable.R_cc_o, 0.0492)
            self.assertEqual(lv_cable.X_ch_o, 0.71)
            self.assertEqual(lv_cable.R_hh_o, 0.33)

    def test_lv_cable_o_suffix_matches_without_rename(self) -> None:
        # The _O spelling reaches the same field through case matching alone.
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path, pd.DataFrame({"Name": ["Cable One"], "R_CC_O": [0.0492]})
            )

            lv_cable = cast("LVCableType", Types(str(path)).get_lv_cable("Cable One"))
            self.assertEqual(lv_cable.R_cc_o, 0.0492)

    def test_default_rename_source_matches_ignoring_case(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path, pd.DataFrame({"Name": ["Cable One"], "TAN_DELTA": [0.07]})
            )

            mv_cable = cast("MVCableType", Types(str(path)).get_mv_cable("Cable One"))
            self.assertEqual(mv_cable.tan_delta, 0.07)

    def test_exact_header_wins_over_relaxed_match(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_cable_sheet(
                path,
                pd.DataFrame({"Name": ["Cable One"], "r": [0.1], "R": [0.2]}),
            )

            cable = cast("MVCableType", Types(str(path)).get_mv_cable("Cable One"))
            self.assertEqual(cable.r, 0.2)

    def test_default_construction_unchanged(self) -> None:
        types = Types()
        self.assertIsInstance(types, Types)


if __name__ == "__main__":
    unittest.main()
