from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pyptp.network_lv import NetworkLV
from pyptp.type_reader import Types, UnknownTypeError
from pyptp.type_reader._gm import gm_row_to_sections


class TestGMRowToSections(unittest.TestCase):
    """Regrouping one sheet row into the sections the element reads."""

    def test_general_carries_name_indicator_and_cos(self) -> None:
        sections = gm_row_to_sections(
            {"Name": "Warmtepomp", "Indicator": "WP", "Cos": 0.9, "Correlation": 0.5}
        )

        general = sections["general"][0]
        self.assertEqual(general["GMtype"], "Warmtepomp")
        self.assertEqual(general["Indicator"], "HP")
        self.assertEqual(general["CosPhi"], 0.9)
        self.assertEqual(general["Correlation"], 0.5)

    def test_indicator_words_map_to_file_format_tokens(self) -> None:
        for word, token in (
            ("Belasting", "Load"),
            ("BelastingProcent", "LoadPercent"),
            ("EV", "EV"),
            ("PV", "PV"),
            ("Koken", "Cooking"),
            ("Apparaat", "Device"),
        ):
            with self.subTest(word=word):
                sections = gm_row_to_sections({"Name": "X", "Indicator": word})
                self.assertEqual(sections["general"][0]["Indicator"], token)

    def test_a_blank_indicator_counts_as_load(self) -> None:
        sections = gm_row_to_sections({"Name": "X", "Indicator": ""})

        self.assertEqual(sections["general"][0]["Indicator"], "Load")

    def test_an_unknown_indicator_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Laadpaal"):
            gm_row_to_sections({"Name": "X", "Indicator": "Laadpaal"})

    def test_a_blank_cos_becomes_one(self) -> None:
        sections = gm_row_to_sections({"Name": "X"})

        self.assertEqual(sections["general"][0]["CosPhi"], 1.0)

    def test_a_distribution_without_values_is_left_out(self) -> None:
        sections = gm_row_to_sections({"Name": "X"})

        self.assertNotIn("gm1", sections)
        self.assertNotIn("workdays1", sections)

    def test_a_distribution_with_values_is_kept(self) -> None:
        sections = gm_row_to_sections(
            {"Name": "X", "Average[2]": 0.7, "Deviation[2]": 0.5}
        )

        self.assertEqual(sections["gm2"][0], {"Average": 0.7, "StandardDeviation": 0.5})

    def test_a_day_series_is_padded_to_a_full_day(self) -> None:
        sections = gm_row_to_sections({"Name": "X", "Workday[1,3]": 0.4})

        workdays = sections["workdays1"][0]
        self.assertEqual(len(workdays), 96)
        self.assertEqual(workdays["f3"], 0.4)
        self.assertEqual(workdays["f1"], 0.0)

    def test_a_month_series_holds_twelve_values(self) -> None:
        sections = gm_row_to_sections({"Name": "X", "Month[1,12]": 1.2})

        self.assertEqual(len(sections["months1"][0]), 12)

    def test_trend_series_are_read(self) -> None:
        sections = gm_row_to_sections(
            {"Name": "X", "TrendWorkday[5]": 1.1, "TrendMonth[2]": 0.9}
        )

        self.assertEqual(sections["trendworkdays"][0]["f5"], 1.1)
        self.assertEqual(sections["trendmonths"][0]["f2"], 0.9)
        self.assertNotIn("trendweekenddays", sections)

    def test_a_cell_that_is_not_a_number_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "0,7"):
            gm_row_to_sections({"Name": "X", "Average[1]": "0,7"})


class TestGMTypeLookup(unittest.TestCase):
    """Reading GM types from the bundled workbook."""

    def setUp(self) -> None:
        self.types = Types()

    def test_a_standard_consumption_type(self) -> None:
        gm_type = self.types.get_lv_gm_type("sjv3000")

        self.assertEqual(gm_type.general.type, "sjv3000")
        self.assertEqual(gm_type.general.indicator, "Load")
        self.assertEqual(len(gm_type.gm1_workdays), 96)
        self.assertEqual(len(gm_type.gm1_weekenddays), 96)
        self.assertEqual(len(gm_type.gm1_months), 12)

    def test_a_heat_pump_type(self) -> None:
        gm_type = self.types.get_lv_gm_type("Warmtepomp")

        self.assertEqual(gm_type.general.indicator, "HP")
        self.assertEqual(gm_type.general.cos_phi, 0.9)

    def test_unknown_name_raises(self) -> None:
        with self.assertRaises(UnknownTypeError):
            self.types.get_lv_gm_type("sjv999999")

    def test_an_unreadable_row_names_the_type(self) -> None:
        self.types._rows("lv_gm_type")["sjv3000"]["Indicator"] = "Laadpaal"

        with self.assertRaisesRegex(ValueError, "sjv3000"):
            self.types.get_lv_gm_type("sjv3000")

    def test_an_added_type_survives_a_save_and_reload(self) -> None:
        network = NetworkLV()
        gm_type = network.add(self.types.get_lv_gm_type("sjv3000"))
        number = gm_type.general.number

        with TemporaryDirectory() as td:
            path = Path(td) / "gm.gnf"
            network.save(path)
            reloaded = NetworkLV.from_file(path).gmtypes[number]

        self.assertEqual(reloaded.general, gm_type.general)
        self.assertEqual(reloaded.gm1.average, gm_type.gm1.average)
        self.assertEqual(
            reloaded.gm1.standard_deviation, gm_type.gm1.standard_deviation
        )
        self.assertEqual(reloaded.gm1_workdays, gm_type.gm1_workdays)


if __name__ == "__main__":
    unittest.main()
