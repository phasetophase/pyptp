"""Handler for parsing VNF Measure Field sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class MeasureFieldHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Measure Field components using a declarative recipe."""

    COMPONENT_CLS = MeasureFieldMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("voltage_measure_transformer_type", "#VoltageMeasureTransformerType "),
        SectionConfig("current_measure_transformer1_type", "#CurrentMeasureTransformer1Type "),
        SectionConfig("current_measure_transformer2_type", "#CurrentMeasureTransformer2Type "),
        SectionConfig("current_measure_transformer3_type", "#CurrentMeasureTransformer3Type "),
        SectionConfig("measurements", "#Measurement "),
        SectionConfig("measurementfiles", "#MeasurementsFile "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for MeasureField-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import SecondaryPresentation

            return SecondaryPresentation
        if kwarg_name == "measurements":
            return MeasureFieldMV.Measurement
        if kwarg_name == "measurementfiles":
            return MeasureFieldMV.MeasurementsFile
        if kwarg_name == "voltage_measure_transformer_type":
            return MeasureFieldMV.VoltageMeasureTransformerType
        if kwarg_name == "current_measure_transformer1_type":
            return MeasureFieldMV.CurrentMeasureTransformer1Type
        if kwarg_name == "current_measure_transformer2_type":
            return MeasureFieldMV.CurrentMeasureTransformer2Type
        if kwarg_name == "current_measure_transformer3_type":
            return MeasureFieldMV.CurrentMeasureTransformer3Type
        return None
