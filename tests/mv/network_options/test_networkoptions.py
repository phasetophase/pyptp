"""Tests for NetworkOptionsMV serialization, deserialization, handler parsing, and round-trip."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyptp.elements.element_utils import decode_int_list, encode_int_list
from pyptp.elements.mv.network_options import NetworkOptionsMV
from pyptp.IO.importers._vnf_handlers.network_options_handler import (
    NetworkOptionsHandler,
)
from pyptp.network_mv import NetworkMV


class TestNetworkOptionsSerialize(unittest.TestCase):
    """Serialization of NetworkOptionsMV to the VNF #General line."""

    def test_empty_network_options_serializes_to_bare_general(self) -> None:
        network_options = NetworkOptionsMV(general=NetworkOptionsMV.General())
        self.assertEqual("#General ", network_options.serialize())

    def test_winter_profile_items_only(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(winter_profile_items=[1, 2])
        )
        self.assertEqual("#General WinterProfileItems:1,2", network_options.serialize())

    def test_low_tactics_profile_items_only(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(low_tactics_profile_items=[16, 26])
        )
        self.assertEqual(
            "#General LowTacticsProfileItems:16,26", network_options.serialize()
        )

    def test_high_tactics_profile_items_only(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(high_tactics_profile_items=[12])
        )
        self.assertEqual(
            "#General HighTacticsProfileItems:12", network_options.serialize()
        )

    def test_empty_list_for_one_field_is_skipped(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(high_tactics_profile_items=[])
        )
        self.assertEqual("#General ", network_options.serialize())

    def test_all_three_fields_populated(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(
                winter_profile_items=[1, 2],
                low_tactics_profile_items=[16, 26],
                high_tactics_profile_items=[12],
            )
        )
        self.assertEqual(
            "#General WinterProfileItems:1,2 LowTacticsProfileItems:16,26 HighTacticsProfileItems:12",
            network_options.serialize(),
        )

    def test_single_element_list(self) -> None:
        network_options = NetworkOptionsMV(
            general=NetworkOptionsMV.General(winter_profile_items=[7])
        )
        self.assertEqual("#General WinterProfileItems:7", network_options.serialize())


class TestNetworkOptionsDeserialize(unittest.TestCase):
    """Deserialization of the parsed property dict into NetworkOptionsMV.General."""

    def test_all_keys_populated(self) -> None:
        general = NetworkOptionsMV.General.deserialize(
            {
                "WinterProfileItems": "1,2",
                "LowTacticsProfileItems": "16,26",
                "HighTacticsProfileItems": "12",
            }
        )
        self.assertEqual([1, 2], general.winter_profile_items)
        self.assertEqual([16, 26], general.low_tactics_profile_items)
        self.assertEqual([12], general.high_tactics_profile_items)

    def test_missing_keys_default_to_empty_list(self) -> None:
        general = NetworkOptionsMV.General.deserialize({})
        self.assertEqual([], general.winter_profile_items)
        self.assertEqual([], general.low_tactics_profile_items)
        self.assertEqual([], general.high_tactics_profile_items)

    def test_empty_string_values_produce_empty_list(self) -> None:
        general = NetworkOptionsMV.General.deserialize(
            {
                "WinterProfileItems": "",
                "LowTacticsProfileItems": "",
                "HighTacticsProfileItems": "",
            }
        )
        self.assertEqual([], general.winter_profile_items)
        self.assertEqual([], general.low_tactics_profile_items)
        self.assertEqual([], general.high_tactics_profile_items)

    def test_single_element(self) -> None:
        general = NetworkOptionsMV.General.deserialize({"WinterProfileItems": "42"})
        self.assertEqual([42], general.winter_profile_items)


class TestNetworkOptionsHandler(unittest.TestCase):
    """End-to-end handler parsing of NETWORKOPTIONS chunks.

    This exercises the `_base_handler._parse_gnf_line_to_dict` special case
    that keeps comma-separated values as raw strings for these three keys.
    Without it, "1,2" would be parsed as the float 1.2.
    """

    def _run_handler(self, chunk_body: str) -> NetworkMV:
        network = NetworkMV()
        chunk = f"{chunk_body}\n#END"
        NetworkOptionsHandler().handle(network, chunk)
        return network

    def test_handler_parses_all_three_keys(self) -> None:
        network = self._run_handler(
            "#General WinterProfileItems:1,2 LowTacticsProfileItems:16,26 HighTacticsProfileItems:12"
        )
        self.assertIsNotNone(network.network_options)
        assert network.network_options is not None
        general = network.network_options.general
        self.assertEqual([1, 2], general.winter_profile_items)
        self.assertEqual([16, 26], general.low_tactics_profile_items)
        self.assertEqual([12], general.high_tactics_profile_items)

    def test_handler_parses_only_winter(self) -> None:
        network = self._run_handler("#General WinterProfileItems:5,10,15")
        self.assertIsNotNone(network.network_options)
        assert network.network_options is not None
        general = network.network_options.general
        self.assertEqual([5, 10, 15], general.winter_profile_items)
        self.assertEqual([], general.low_tactics_profile_items)
        self.assertEqual([], general.high_tactics_profile_items)

    def test_handler_bare_general_with_trailing_space(self) -> None:
        """'#General ' (trailing space, no properties) parses to empty lists."""
        network = self._run_handler("#General ")
        self.assertIsNotNone(network.network_options)
        assert network.network_options is not None
        general = network.network_options.general
        self.assertEqual([], general.winter_profile_items)
        self.assertEqual([], general.low_tactics_profile_items)
        self.assertEqual([], general.high_tactics_profile_items)

    def test_handler_bare_general_without_trailing_space(self) -> None:
        """'#General' (no trailing space, no properties) parses to empty lists."""
        network = self._run_handler("#General")
        self.assertIsNotNone(network.network_options)
        assert network.network_options is not None
        general = network.network_options.general
        self.assertEqual([], general.winter_profile_items)

    def test_handler_preserves_comma_list_not_parsed_as_float(self) -> None:
        """Regression guard: '1,2' must not collapse to float 1.2.

        This is the whole point of the _base_handler special case for these
        three keys. If someone removes or mistypes that branch, this test
        should fail loudly.
        """
        network = self._run_handler("#General WinterProfileItems:1,2")
        assert network.network_options is not None
        general = network.network_options.general
        self.assertEqual([1, 2], general.winter_profile_items)
        self.assertNotEqual([1], general.winter_profile_items)

    def test_register_twice_replaces_existing(self) -> None:
        """NetworkOptions is a singleton: a second register() replaces the first."""
        network = NetworkMV()
        first = NetworkOptionsMV(
            general=NetworkOptionsMV.General(winter_profile_items=[1])
        )
        second = NetworkOptionsMV(
            general=NetworkOptionsMV.General(winter_profile_items=[2])
        )
        first.register(network)
        second.register(network)
        self.assertIs(second, network.network_options)


class TestNetworkOptionsRoundtrip(unittest.TestCase):
    """Full save + load round-trip through VnfExporter and VnfImporter."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.output_file = self.tmp_path / "network_options_roundtrip.vnf"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _build_network_with_options(
        self, general: NetworkOptionsMV.General
    ) -> NetworkMV:
        network = NetworkMV()
        NetworkOptionsMV(general=general).register(network)
        return network

    def _roundtrip(self, general: NetworkOptionsMV.General) -> NetworkOptionsMV.General:
        network = self._build_network_with_options(general)
        network.save(self.output_file)
        reloaded = NetworkMV.from_file(self.output_file)
        self.assertIsNotNone(
            reloaded.network_options, "NETWORKOPTIONS expected after reload"
        )
        assert reloaded.network_options is not None
        return reloaded.network_options.general

    def _save_and_read_file(self, general: NetworkOptionsMV.General) -> str:
        network = self._build_network_with_options(general)
        network.save(self.output_file)
        return self.output_file.read_text(encoding="utf-8")

    def test_roundtrip_all_three_fields(self) -> None:
        original = NetworkOptionsMV.General(
            winter_profile_items=[1, 2, 3],
            low_tactics_profile_items=[10, 20],
            high_tactics_profile_items=[99],
        )
        reloaded = self._roundtrip(original)
        self.assertEqual(original.winter_profile_items, reloaded.winter_profile_items)
        self.assertEqual(
            original.low_tactics_profile_items, reloaded.low_tactics_profile_items
        )
        self.assertEqual(
            original.high_tactics_profile_items, reloaded.high_tactics_profile_items
        )

    def test_roundtrip_winter_only(self) -> None:
        original = NetworkOptionsMV.General(winter_profile_items=[1, 2])
        reloaded = self._roundtrip(original)
        self.assertEqual([1, 2], reloaded.winter_profile_items)
        self.assertEqual([], reloaded.low_tactics_profile_items)
        self.assertEqual([], reloaded.high_tactics_profile_items)

    def test_empty_options_are_not_written(self) -> None:
        """An all-empty NetworkOptions should be skipped at export, not emitted as a bare #General."""
        content = self._save_and_read_file(NetworkOptionsMV.General())
        self.assertNotIn("[NETWORKOPTIONS]", content)

    def test_roundtrip_empty_options_drops_the_section(self) -> None:
        """Empty options are not written, so on reload the network has no options."""
        network = self._build_network_with_options(NetworkOptionsMV.General())
        network.save(self.output_file)
        reloaded = NetworkMV.from_file(self.output_file)
        self.assertIsNone(reloaded.network_options)

    def test_roundtrip_single_element(self) -> None:
        original = NetworkOptionsMV.General(high_tactics_profile_items=[7])
        reloaded = self._roundtrip(original)
        self.assertEqual([7], reloaded.high_tactics_profile_items)


class TestEncodeDecodeIntList(unittest.TestCase):
    """Unit tests for the encode/decode helpers used by network_options."""

    def test_encode_empty_list(self) -> None:
        self.assertEqual("", encode_int_list([]))

    def test_encode_single(self) -> None:
        self.assertEqual("5", encode_int_list([5]))

    def test_encode_multiple(self) -> None:
        self.assertEqual("1,2,3", encode_int_list([1, 2, 3]))

    def test_decode_empty_string(self) -> None:
        self.assertEqual([], decode_int_list(""))

    def test_decode_whitespace_only(self) -> None:
        self.assertEqual([], decode_int_list("   "))

    def test_decode_single(self) -> None:
        self.assertEqual([5], decode_int_list("5"))

    def test_decode_multiple(self) -> None:
        self.assertEqual([1, 2, 3], decode_int_list("1,2,3"))

    def test_decode_strips_whitespace_between_items(self) -> None:
        self.assertEqual([1, 2, 3], decode_int_list("1, 2 , 3"))

    def test_encode_then_decode_roundtrip(self) -> None:
        original = [0, 1, 42, 1000]
        self.assertEqual(original, decode_int_list(encode_int_list(original)))


if __name__ == "__main__":
    unittest.main()
