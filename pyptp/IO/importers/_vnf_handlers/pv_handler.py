"""Handler for parsing VNF PV sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.pv import PVMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class PvHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF PV components using a declarative recipe."""

    COMPONENT_CLS = PVMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("inverter", "#Inverter ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("efficiency_type", "#EfficiencyType "),
        SectionConfig("harmonics_type", "#HarmonicsType "),
        SectionConfig("q_control", "#QControl "),
        SectionConfig("pu_control", "#P(U)Control "),
        SectionConfig("pf_control", "#P(f)Control "),
        SectionConfig("pi_control", "#P(I)Control "),
        SectionConfig("inverter_efficiency", "#InverterRendement "),
        SectionConfig("restrictions", "#Restriction "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for PV-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "inverter":
            return PVMV.Inverter
        if kwarg_name == "efficiency_type":
            from pyptp.elements.mv.shared import EfficiencyType

            return EfficiencyType
        if kwarg_name == "harmonics_type":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        if kwarg_name == "q_control":
            from pyptp.elements.mv.shared import QControl

            return QControl
        if kwarg_name == "pu_control":
            return PVMV.PUControl
        if kwarg_name == "pf_control":
            return PVMV.PFControl
        if kwarg_name == "pi_control":
            return PVMV.PIControl
        if kwarg_name == "inverter_efficiency":
            from pyptp.elements.mv.shared import EfficiencyType

            return EfficiencyType
        if kwarg_name == "restrictions":
            return PVMV.Capacity
        return None
