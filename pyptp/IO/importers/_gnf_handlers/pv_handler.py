"""Handler for parsing GNF PV sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.pv import PVLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class PvHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF PV components using a declarative recipe."""

    COMPONENT_CLS = PVLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("inverter", "#Inverter "),
        SectionConfig("efficiency_type", "#EfficiencyType "),
        SectionConfig("q_control", "#QControl "),
        SectionConfig("pu_control", "#P(U)Control "),
        SectionConfig("harmonics", "#HarmonicsType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for PV-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "inverter":
            return PVLV.Inverter
        if kwarg_name == "efficiency_type":
            from pyptp.elements.lv.shared import EfficiencyType

            return EfficiencyType
        if kwarg_name == "q_control":
            return PVLV.QControl
        if kwarg_name == "pu_control":
            return PVLV.PUControl
        if kwarg_name == "harmonics":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
