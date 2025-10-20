"""Handler for parsing VNF Battery sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.battery import BatteryMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class BatteryHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Battery components using a declarative recipe."""

    COMPONENT_CLS = BatteryMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("inverter", "#Inverter ", required=True),
        SectionConfig("p_control", "#PControl "),
        SectionConfig("q_control", "#QControl "),
        SectionConfig("charge_efficiency_type", "#ChargeEfficiencyType "),
        SectionConfig("discharge_efficiency_type", "#DischargeEfficiencyType "),
        SectionConfig("harmonics_type", "#HarmonicsType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Battery-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "inverter":
            return BatteryMV.Inverter
        if kwarg_name == "p_control":
            from pyptp.elements.mv.shared import PControl

            return PControl
        if kwarg_name == "q_control":
            from pyptp.elements.mv.shared import QControl

            return QControl
        if kwarg_name in {"charge_efficiency_type", "discharge_efficiency_type"}:
            from pyptp.elements.mv.shared import EfficiencyType

            return EfficiencyType
        if kwarg_name == "harmonics_type":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
