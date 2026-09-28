from __future__ import annotations

import unittest

from pyptp.elements.lv.connection import ConnectionLV
from pyptp.network_lv import NetworkLV
from pyptp.validator.lv.connection_load_phases import ConnectionLoadPhasesValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestConnectionLoadPhasesLV(unittest.TestCase):
    """LV connection load phase validation."""

    def _network(
        self,
        phases: int,
        load: ConnectionLV.Load | None,
        generation: ConnectionLV.Generation | None = None,
    ) -> NetworkLV:
        network = NetworkLV()
        network.add(
            ConnectionLV(
                general=ConnectionLV.General(name="Woning", phases=phases),
                presentations=[],
                gms=[],
                load=load,
                generation=generation,
            )
        )
        return network

    def test_three_phase_load_on_three_phase_connection(self) -> None:
        network = self._network(4, ConnectionLV.Load(pa=0.001, pb=0.001, pc=0.001))

        assert_no_validation_issues(self, ConnectionLoadPhasesValidator(), network)

    def test_single_phase_load_on_single_phase_connection(self) -> None:
        network = self._network(1, ConnectionLV.Load(p1=0.003))

        assert_no_validation_issues(self, ConnectionLoadPhasesValidator(), network)

    def test_single_phase_load_on_three_phase_connection_warns(self) -> None:
        network = self._network(4, ConnectionLV.Load(p1=0.003))

        issues = ConnectionLoadPhasesValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "load_ignored_for_phases")
        self.assertIn("is three-phase", issues[0].message)
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["part"], "load")
        self.assertEqual(issues[0].details["ignored_fields"], ["p1"])

    def test_three_phase_load_on_single_phase_connection_warns(self) -> None:
        network = self._network(2, ConnectionLV.Load(pab=0.002, qab=0.001))

        issues = ConnectionLoadPhasesValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertIn("is single-phase", issues[0].message)
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["ignored_fields"], ["pab", "qab"])

    def test_three_phase_generation_on_single_phase_connection_warns(self) -> None:
        load = ConnectionLV.Load(p1=0.003)
        generation = ConnectionLV.Generation(pa=0.002, pb=0.002)
        network = self._network(1, load, generation)

        issues = ConnectionLoadPhasesValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertIn("its generation in pa, pb is ignored", issues[0].message)
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["part"], "generation")
        self.assertEqual(issues[0].details["ignored_fields"], ["pa", "pb"])

    def test_connection_without_load_is_skipped(self) -> None:
        network = self._network(4, None)

        assert_no_validation_issues(self, ConnectionLoadPhasesValidator(), network)

    def test_empty_load_is_not_reported(self) -> None:
        network = self._network(4, ConnectionLV.Load())

        assert_no_validation_issues(self, ConnectionLoadPhasesValidator(), network)

    def test_one_issue_per_connection(self) -> None:
        network = self._network(4, ConnectionLV.Load(p1=0.003, q1=0.001))

        issues = ConnectionLoadPhasesValidator().validate(network)
        self.assertEqual(len(issues), 1)
        assert issues[0].details is not None
        self.assertEqual(issues[0].details["ignored_fields"], ["p1", "q1"])


if __name__ == "__main__":
    unittest.main()
