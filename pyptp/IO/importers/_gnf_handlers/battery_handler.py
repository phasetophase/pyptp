"""Handler for parsing GNF Battery sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.battery import BatteryLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class BatteryHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Battery components using a declarative recipe."""

    COMPONENT_CLS = BatteryLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("inverter", "#Inverter "),
        SectionConfig("pu_control", "#P(U)Control "),
        SectionConfig("pi_control", "#P(I)Control "),
        SectionConfig("charge_efficiency", "#ChargeEfficiencyType "),
        SectionConfig("discharge_efficiency", "#DischargeEfficiencyType "),
        SectionConfig("harmonics", "#HarmonicsType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Battery-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "inverter":
            return BatteryLV.Inverter
        if kwarg_name == "pu_control":
            return BatteryLV.PUControl
        if kwarg_name == "pi_control":
            return BatteryLV.PIControl
        if kwarg_name in ("charge_efficiency", "discharge_efficiency"):
            from pyptp.elements.lv.shared import EfficiencyType

            return EfficiencyType
        if kwarg_name == "harmonics":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
