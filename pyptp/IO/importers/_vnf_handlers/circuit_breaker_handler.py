"""Handler for parsing VNF Circuit Breaker sections using a declarative recipe."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pyptp.elements.mv.circuit_breaker import CircuitBreakerMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV

if TYPE_CHECKING:
    from pyptp.elements.element_utils import Guid


class _GuidProcessor:
    """Simple processor to extract GUID values from VNF Object fields."""

    @classmethod
    def deserialize(cls, data: dict) -> Guid:
        """Extract GUID from Object field and convert to Guid type."""
        from pyptp.elements.element_utils import NIL_GUID, decode_guid
        from pyptp.ptp_log import logger

        guid_str = data.get("Object", "")
        if not guid_str or guid_str.isspace():
            logger.warning("Empty or whitespace-only GUID in Object field, using NIL_GUID")
            return NIL_GUID

        try:
            return decode_guid(guid_str)
        except (ValueError, TypeError) as e:
            logger.warning("Failed to parse GUID %r: %s, using NIL_GUID", guid_str, e)
            return NIL_GUID


class _BlockProtectionProcessor:
    """Processor for block protection tuples."""

    @classmethod
    def deserialize(cls, data: dict) -> tuple[int, Guid, int]:
        """Extract block protection tuple from parsed data."""
        from pyptp.elements.element_utils import NIL_GUID, decode_guid
        from pyptp.ptp_log import logger

        guid_str = data.get("BlockCircuitBreaker", "")
        try:
            guid = decode_guid(guid_str) if guid_str and not guid_str.isspace() else NIL_GUID
        except (ValueError, TypeError) as e:
            logger.warning("Failed to parse BlockCircuitBreaker GUID %r: %s, using NIL_GUID", guid_str, e)
            guid = NIL_GUID

        return (data.get("ProtectionIndex", 0), guid, data.get("BlockProtectionIndex", 0))


class _TransferTripProcessor:
    """Processor for transfer trip tuples."""

    @classmethod
    def deserialize(cls, data: dict) -> tuple[int, Guid]:
        """Extract transfer trip tuple from parsed data."""
        from pyptp.elements.element_utils import NIL_GUID, decode_guid
        from pyptp.ptp_log import logger

        guid_str = data.get("TransferCircuitBreaker", "")
        try:
            guid = decode_guid(guid_str) if guid_str and not guid_str.isspace() else NIL_GUID
        except (ValueError, TypeError) as e:
            logger.warning("Failed to parse TransferCircuitBreaker GUID %r: %s, using NIL_GUID", guid_str, e)
            guid = NIL_GUID

        return (data.get("ProtectionIndex", 0), guid)


class CircuitBreakerHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Circuit Breaker components using a declarative recipe."""

    COMPONENT_CLS = CircuitBreakerMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#CircuitBreakerType "),
        SectionConfig("current_protection1_type", "#CurrentProtection1Type "),
        SectionConfig("current_protection2_type", "#CurrentProtection2Type "),
        SectionConfig("earth_fault_protection1_type", "#EarthFaultProtection1Type "),
        SectionConfig("earth_fault_protection2_type", "#EarthFaultProtection2Type "),
        SectionConfig("unbalance_protection_type", "#UnbalanceProtectionType "),
        SectionConfig("thermal_protection", "#ThermalProtection "),
        SectionConfig("voltage_protection", "#VoltageProtectionType "),
        SectionConfig("distance_protection", "#DistanceProtectionType "),
        SectionConfig("differential_protection_type", "#DifferentialProtectionType "),
        SectionConfig("differential_measure_points", "#DifferentialProtectionMeasurePoint "),
        SectionConfig("earth_fault_differential_protection", "#EarthFaultDifferentialProtection "),
        SectionConfig("vector_shift_protection", "#VectorJumpProtection "),
        SectionConfig("frequency_protection", "#FrequencyProtection "),
        SectionConfig("block_protections", "#BlockProtection "),
        SectionConfig("reserve_switches", "#ReserveSwitch "),
        SectionConfig("transfer_trip_switches", "#TransferTripSwitch "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:  # noqa: PLR0911
        """Resolve target class for CircuitBreaker-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import SecondaryPresentation

            return SecondaryPresentation
        if kwarg_name == "type":
            return CircuitBreakerMV.CircuitBreakerType
        # Separate Protection and ProtectionType instances
        if kwarg_name in [
            "currentProtection1",
            "currentProtection2",
            "earthFaultProtection1",
            "earthFaultProtection2",
            "unbalanceProtection",
        ]:
            return CircuitBreakerMV.Protection
        if kwarg_name in [
            "current_protection1_type",
            "current_protection2_type",
            "earth_fault_protection1_type",
            "earth_fault_protection2_type",
            "unbalance_protection_type",
        ]:
            return CircuitBreakerMV.ProtectionType
        if kwarg_name == "thermal_protection":
            return CircuitBreakerMV.ThermalProtection
        if kwarg_name == "voltage_protection":
            return CircuitBreakerMV.VoltageProtectionType
        if kwarg_name == "distance_protection":
            return CircuitBreakerMV.DistanceProtectionType
        if kwarg_name == "differential_protection_type":
            return CircuitBreakerMV.DifferentialProtectionType
        if kwarg_name == "earth_fault_differential_protection":
            return CircuitBreakerMV.EarthFaultDifferentialProtection
        if kwarg_name == "vector_shift_protection":
            return CircuitBreakerMV.VectorShiftProtection
        if kwarg_name in ["differential_measure_points", "reserve_switches"]:
            return _GuidProcessor
        if kwarg_name == "block_protections":
            return _BlockProtectionProcessor
        if kwarg_name == "transfer_trip_switches":
            return _TransferTripProcessor
        if kwarg_name == "frequency_protection":
            return CircuitBreakerMV.FrequencyProtection
        return None
