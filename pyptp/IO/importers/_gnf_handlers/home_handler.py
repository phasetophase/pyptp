"""Handler for parsing GNF Home sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.presentations import ElementPresentation
from pyptp.elements.lv.shared import CableType, CurrentType, EfficiencyType, FuseType
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class HomeHandler(DeclarativeHandler[NetworkLV]):
    COMPONENT_CLS = ConnectionLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("gms", "#GM "),
        SectionConfig("connection_cable", "#ConnectionCableType "),
        SectionConfig("connection_geography", "#ConnectionGeo "),
        SectionConfig("fuse_type", "#FuseType "),
        SectionConfig("current_protection", "#CurrentType "),
        SectionConfig("load", "#Load "),
        SectionConfig("public_lighting", "#PL "),
        SectionConfig("public_lighting_type", "#PLType "),
        SectionConfig("heat_pump", "#Heatpump "),
        SectionConfig("generation", "#Generation "),
        SectionConfig("pv", "#PV "),
        SectionConfig("pv_efficiency", "#PVInverterEfficiencyType "),
        SectionConfig("windturbine", "#WindTurbine "),
        SectionConfig("windturbine_efficiency", "#WindTurbineInverterEfficiencyType "),
        SectionConfig("battery", "#Battery "),
        SectionConfig("battery_charge_efficiency", "#BatteryChargeEfficiency "),
        SectionConfig("battery_discharge_efficiency", "#BatteryDischargeEfficiency "),
        SectionConfig("hems", "#Hems "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Home-specific fields."""
        if kwarg_name == "presentations":
            return ElementPresentation
        if kwarg_name == "connection_cable":
            return CableType
        if kwarg_name == "current_protection":
            return CurrentType
        if kwarg_name == "fuse_type":
            return FuseType
        if kwarg_name == "connection_geography":
            return ConnectionLV.Geography
        if kwarg_name == "public_lighting":
            return ConnectionLV.PL
        if kwarg_name == "public_lighting_type":
            return ConnectionLV.PLType
        if kwarg_name == "heat_pump":
            return ConnectionLV.Heatpump
        if kwarg_name == "gms":
            return ConnectionLV.GM
        if kwarg_name in [
            "pv_efficiency",
            "windturbine_efficiency",
            "battery_charge_efficiency",
            "battery_discharge_efficiency",
        ]:
            return EfficiencyType
        return None
