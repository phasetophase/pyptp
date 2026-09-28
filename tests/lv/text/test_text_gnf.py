"""Tests for TextLV and HyperlinkLV GNF import and export."""

import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.hyperlink import HyperlinkLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.text import TextLV
from pyptp.IO.exporters.gnf_exporter import GnfExporter
from pyptp.IO.importers.gnf_importer import GnfImporter
from pyptp.network_lv import NetworkLV

TEXT_GUID = Guid(UUID("11111111-2222-3333-4444-555555555555"))
SHEET_GUID = Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2"))


class TestTextAndHyperlinkGnf(unittest.TestCase):
    """Round-trip a network with a text and two hyperlinks through GNF."""

    def setUp(self) -> None:
        """Create a network with one sheet, one text and two hyperlinks."""
        self.network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=SHEET_GUID, name="TestSheet"))
        sheet.register(self.network)

        text = TextLV(
            general=TextLV.General(
                guid=TEXT_GUID, creation_time=45000.5, mutation_date=45001
            ),
            lines=["First line with 'quotes' and Key:Value", "", "third"],
            presentations=[
                TextLV.Presentation(
                    sheet=SHEET_GUID,
                    x=100,
                    y=-20,
                    text_size=12,
                    font="Courier",
                    text_style=3,
                    upside_down_text=True,
                ),
                TextLV.Presentation(sheet=SHEET_GUID),
            ],
        )
        text.register(self.network)

        HyperlinkLV(url="C:\\data\\Data.txt").register(self.network)
        HyperlinkLV(url="https://example.org/x y").register(self.network)

    def _export_to_temp(self) -> Path:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".gnf", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)
        GnfExporter.export(self.network, str(tmp_path))
        return tmp_path

    def test_export_writes_text_and_hyperlink_sections(self) -> None:
        """Exported GNF contains the TEXT and HYPERLINKS sections in Gaia's format."""
        tmp_path = self._export_to_temp()
        try:
            content = tmp_path.read_text(encoding="utf-8-sig")
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertIn("[HYPERLINKS]\n#Hyperlink URL:'C:\\data\\Data.txt'", content)
        self.assertIn("#Hyperlink URL:'https://example.org/x y'", content)
        self.assertIn(
            "[TEXT]\n#General GUID:'{11111111-2222-3333-4444-555555555555}'", content
        )
        self.assertIn(
            "#Line Text:First line with 'quotes' and Key:Value\n#Line Text:\n#Line Text:third\n",
            content,
        )
        self.assertIn(
            "X:100 Y:-20 TextSize:12 Font:'Courier' TextStyle:3 UpsideDownText:True",
            content,
        )
        # HYPERLINKS follows COMMENTS and TEXT precedes FRAME/LEGEND/SELECTION, as in Gaia.
        self.assertLess(content.index("[COMMENTS]"), content.index("[HYPERLINKS]"))
        self.assertLess(content.index("[HYPERLINKS]"), content.index("[SHEET]"))
        self.assertLess(content.index("[SHEET]"), content.index("[TEXT]"))

    def test_empty_sections_are_omitted(self) -> None:
        """A network without texts or hyperlinks writes neither section."""
        self.network.texts.clear()
        self.network.hyperlinks.clear()
        tmp_path = self._export_to_temp()
        try:
            content = tmp_path.read_text(encoding="utf-8-sig")
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertNotIn("[TEXT]", content)
        self.assertNotIn("[HYPERLINKS]", content)

    def test_import_export_roundtrip(self) -> None:
        """Importing the exported file reproduces the text and hyperlinks."""
        tmp_path = self._export_to_temp()
        try:
            imported = GnfImporter().import_gnf(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertEqual(
            [h.url for h in imported.hyperlinks],
            ["C:\\data\\Data.txt", "https://example.org/x y"],
        )

        self.assertEqual(list(imported.texts), [TEXT_GUID])
        text = imported.texts[TEXT_GUID]
        original = self.network.texts[TEXT_GUID]
        self.assertEqual(text.general.creation_time, 45000.5)
        self.assertEqual(text.general.mutation_date, 45001)
        self.assertEqual(text.lines, original.lines)
        self.assertEqual(len(text.presentations), 2)

        styled, plain = text.presentations
        self.assertEqual(styled.sheet, SHEET_GUID)
        self.assertEqual(
            (styled.x, styled.y, styled.text_size, styled.font),
            (100, -20, 12, "Courier"),
        )
        self.assertEqual(styled.text_style, 3)
        self.assertTrue(styled.upside_down_text)
        self.assertEqual(
            (plain.x, plain.y, plain.text_size, plain.font), (0, 0, 10, "Arial")
        )
        self.assertFalse(plain.upside_down_text)


if __name__ == "__main__":
    unittest.main()
