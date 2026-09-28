from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.fuse import FuseMV
from pyptp.elements.mv.transformer import TransformerMV
from pyptp.type_reader import Types, UnknownTypeError

CABLE = "4* 50 VMvK/Alk"
FUSE = "Voorbeeld 35 A"
TRANSFORMER = "10250/400 V  630 kVA"

TRAFO_NAME = "10250/400 V   50 kVA"
TRAFO_ALIAS = "50kVA"
CABLE_NAME = "Cable One"
CABLE_ALIAS = "CABLE_ALIAS"


def _write_alias_workbook(path: Path) -> None:
    """Write a workbook with one transformer, one cable and an alias for each."""
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(
            {"Name": [TRAFO_NAME], "Shortname": ["50 kVA"], "Snom": [0.05]}
        ).to_excel(writer, sheet_name="Trafo", index=False)
        pd.DataFrame({"Alias": [TRAFO_ALIAS], "Name": [TRAFO_NAME]}).set_index(
            "Alias"
        ).to_excel(writer, sheet_name="Trafo alias")
        pd.DataFrame(
            {"Name": [CABLE_NAME], "Shortname": ["C1"], "R_C": [0.1]}
        ).to_excel(writer, sheet_name="Cable", index=False)
        pd.DataFrame({"Alias": [CABLE_ALIAS], "Name": [CABLE_NAME]}).set_index(
            "Alias"
        ).to_excel(writer, sheet_name="Cable alias")


class TestTypeSettersLV(unittest.TestCase):
    """Setters that name a type and attach its data."""

    def setUp(self) -> None:
        self.types = Types()

    def test_cable_set_cable_type_keeps_the_full_name(self) -> None:
        cable = CableLV(
            general=CableLV.General(name="K1"),
            presentations=[],
            cable_part=CableLV.CablePart(length=15.0),
        )

        cable.set_cable_type(self.types, CABLE)

        self.assertEqual(cable.cable_part.type, CABLE)
        assert cable.cable_type is not None
        self.assertEqual(cable.cable_type.R_c, 0.6903)

    def test_cable_set_cable_type_unknown_raises(self) -> None:
        cable = CableLV(
            general=CableLV.General(name="K1"),
            presentations=[],
            cable_part=CableLV.CablePart(length=15.0),
        )

        with self.assertRaises(UnknownTypeError):
            cable.set_cable_type(self.types, "geen kabeltype")
        self.assertIsNone(cable.cable_type)

    def test_two_cables_of_one_type_hold_separate_type_objects(self) -> None:
        first = CableLV(
            general=CableLV.General(name="K1"),
            presentations=[],
            cable_part=CableLV.CablePart(length=15.0),
        )
        second = CableLV(
            general=CableLV.General(name="K2"),
            presentations=[],
            cable_part=CableLV.CablePart(length=25.0),
        )

        first.set_cable_type(self.types, CABLE)
        second.set_cable_type(self.types, CABLE)

        self.assertEqual(first.cable_type, second.cable_type)
        self.assertIsNot(first.cable_type, second.cable_type)

    def test_fuse_set_type_fills_the_name_too(self) -> None:
        fuse = FuseLV(general=FuseLV.General(name="F1"))

        fuse.set_type(self.types, FUSE)

        self.assertEqual(fuse.general.type, FUSE)
        assert fuse.type is not None
        self.assertEqual(fuse.type.inom, 35)

    def test_transformer_set_type(self) -> None:
        transformer = TransformerLV(
            general=TransformerLV.General(name="T1"),
            presentations=[],
            type=TransformerLV.TransformerType(),
        )

        transformer.set_type(self.types, TRANSFORMER)

        self.assertEqual(transformer.general.type, TRANSFORMER)
        self.assertEqual(transformer.type.short_name, "630 kVA")

    def test_connection_set_cable_and_fuse_type(self) -> None:
        connection = ConnectionLV(
            general=ConnectionLV.General(name="W1"), presentations=[], gms=[]
        )

        connection.set_cable_type(self.types, CABLE)
        connection.set_fuse_type(self.types, FUSE)

        self.assertEqual(connection.general.cable_type, CABLE)
        assert connection.connection_cable is not None
        self.assertEqual(connection.connection_cable.R_c, 0.6903)
        self.assertEqual(connection.general.protection_type, FUSE)
        assert connection.fuse_type is not None
        self.assertEqual(connection.fuse_type.inom, 35)


class TestTypeSettersMV(unittest.TestCase):
    """MV setters."""

    def setUp(self) -> None:
        self.types = Types()

    def test_fuse_set_type(self) -> None:
        fuse = FuseMV(
            general=FuseMV.General(name="F1"), type=FuseMV.FuseType(), presentations=[]
        )

        fuse.set_type(self.types, FUSE)

        self.assertEqual(fuse.general.type, FUSE)
        self.assertEqual(fuse.type.inom, 35)

    def test_transformer_set_type(self) -> None:
        transformer = TransformerMV(
            general=TransformerMV.General(name="T1"),
            presentations=[],
            type=TransformerMV.TransformerType(),
        )

        transformer.set_type(self.types, TRANSFORMER)

        self.assertEqual(transformer.general.type, TRANSFORMER)
        self.assertEqual(transformer.type.short_name, "630 kVA")

    def test_cable_add_part_keeps_parts_and_types_in_step(self) -> None:
        cable = CableMV(
            general=CableMV.General(name="K1"),
            presentations=[],
            cable_parts=[],
            cable_types=[],
        )
        part = cable.add_part(self.types, CABLE, 120.0)

        self.assertEqual(len(cable.cable_parts), 1)
        self.assertEqual(len(cable.cable_types), 1)
        self.assertEqual(part.cable_type, CABLE)
        self.assertEqual(part.length, 120.0)

    def test_cable_add_part_unknown_raises(self) -> None:
        cable = CableMV(
            general=CableMV.General(name="K1"),
            presentations=[],
            cable_parts=[],
            cable_types=[],
        )

        with self.assertRaises(UnknownTypeError):
            cable.add_part(self.types, "geen kabeltype", 120.0)
        self.assertEqual(cable.cable_parts, [])
        self.assertEqual(cable.cable_types, [])


class TestSettersStoreTheTypeName(unittest.TestCase):
    """Setting a type by alias stores the Name from the workbook."""

    def test_transformer_stores_the_type_name(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_alias_workbook(path)
            types = Types(str(path))

            transformer = TransformerLV(
                general=TransformerLV.General(name="T1"),
                presentations=[],
                type=TransformerLV.TransformerType(),
            )
            transformer.set_type(types, TRAFO_ALIAS)

            self.assertEqual(transformer.general.type, TRAFO_NAME)

    def test_cable_stores_the_type_name(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "wb.xlsx"
            _write_alias_workbook(path)
            types = Types(str(path))

            cable = CableLV(
                general=CableLV.General(name="K1"),
                presentations=[],
                cable_part=CableLV.CablePart(length=15.0),
            )
            cable.set_cable_type(types, CABLE_ALIAS)

            self.assertEqual(cable.cable_part.type, CABLE_NAME)


if __name__ == "__main__":
    unittest.main()
