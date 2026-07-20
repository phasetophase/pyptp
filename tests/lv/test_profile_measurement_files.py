"""Tests for LV profile/measurement file references and native G8.12 import.

Covers the Gaia 8.11 [PROFILEFILES]/[MEASUREMENTFILES] sections ported to the LV
side, plus a native (non-migrated) G8.12 import exercising every 8.12 addition.
"""

import unittest
from pathlib import Path

from pyptp import NetworkLV
from pyptp.elements.element_utils import NIL_GUID
from pyptp.elements.lv.measurement_file import MeasurementFileLV
from pyptp.elements.lv.profile_file import ProfileFileLV
from pyptp.IO.importers._gnf_handlers.measurement_file_handler import (
    MeasurementFileHandler,
)
from pyptp.IO.importers._gnf_handlers.profile_file_handler import ProfileFileHandler


class TestProfileMeasurementFiles(unittest.TestCase):
    """Profile/measurement file references serialize, parse, and register."""

    def test_profile_file_serialize(self) -> None:
        """Profile file serializes as an unquoted #File FileName line."""
        self.assertEqual(
            ProfileFileLV(filename="profiles/example.prf").serialize(),
            "#File FileName:profiles/example.prf",
        )

    def test_measurement_file_serialize(self) -> None:
        """Measurement file serializes as an unquoted #File FileName line."""
        self.assertEqual(
            MeasurementFileLV(filename="measurements/example.msr").serialize(),
            "#File FileName:measurements/example.msr",
        )

    def test_profile_file_round_trip_through_handler(self) -> None:
        """Profile files parse from a PROFILEFILES chunk and register in order."""
        network = NetworkLV()
        chunk = "#File FileName:a.prf\n#File FileName:b/c.prf\n#END"
        ProfileFileHandler().handle(network, chunk)

        self.assertEqual(
            [pf.filename for pf in network.profile_files], ["a.prf", "b/c.prf"]
        )

    def test_measurement_file_round_trip_through_handler(self) -> None:
        """Measurement files parse from a MEASUREMENTFILES chunk and register in order."""
        network = NetworkLV()
        chunk = "#File FileName:m1.msr\n#File FileName:sub/m2.msr\n#END"
        MeasurementFileHandler().handle(network, chunk)

        self.assertEqual(
            [mf.filename for mf in network.measurement_files], ["m1.msr", "sub/m2.msr"]
        )

    def test_register_appends_to_network_lists(self) -> None:
        """register() appends to the network's profile/measurement file lists."""
        network = NetworkLV()
        ProfileFileLV(filename="p.prf").register(network)
        MeasurementFileLV(filename="m.msr").register(network)

        self.assertEqual(len(network.profile_files), 1)
        self.assertEqual(len(network.measurement_files), 1)


class TestNativeG812Import(unittest.TestCase):
    """A native G8.12 file parses without migration and reads every 8.12 addition."""

    def setUp(self) -> None:
        """Locate the G8.12 AllComponents fixture."""
        self.fixture = (
            Path(__file__).parent.parent / "input_files" / "AllComponents_v812.gnf"
        )

    def test_fixture_is_native_g812(self) -> None:
        """The fixture header is G8.12 so it is parsed natively (no DLL migration)."""
        header = self.fixture.read_text(encoding="utf-8-sig").splitlines()[0]
        self.assertEqual(header, "G8.12")

    def test_native_import_reads_new_properties(self) -> None:
        """A native G8.12 import surfaces all the new 8.12 fields and sections."""
        network = NetworkLV.from_file(self.fixture)

        # 8.11 file-reference sections ported to LV.
        self.assertEqual(
            [pf.filename for pf in network.profile_files], ["profiles/example.prf"]
        )
        self.assertEqual(
            [mf.filename for mf in network.measurement_files],
            ["measurements/example.msr"],
        )

        # GM TYPE DefaultP.
        gm = next(iter(network.gmtypes.values()))
        self.assertEqual(gm.general.default_p, 1.5)

        # HOME heatpump HouseYear.
        home = next(iter(network.homes.values()))
        assert home.heat_pump is not None
        self.assertEqual(home.heat_pump.house_year, 1990)

        # SELECTION General GUID.
        self.assertEqual(len(network.selections), 1)
        selection = network.selections[0]
        self.assertEqual(
            str(selection.general.guid).upper(), "5D3E8A1C-7B42-4F96-A0D1-3C88B25E6F47"
        )

        # BATTERY coexisting P(U) and P(I) control with a measure field.
        battery = next(iter(network.batteries.values()))
        assert battery.pu_control is not None
        assert battery.pi_control is not None
        self.assertEqual(battery.pu_control.input1, 0.9)
        self.assertEqual(battery.pi_control.output1, 0.8)
        self.assertNotEqual(battery.pi_control.measure_field1, NIL_GUID)


if __name__ == "__main__":
    unittest.main()
