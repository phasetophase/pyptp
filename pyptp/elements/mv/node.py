"""Medium-voltage network node element for Vision integration.

Provides MV node representation with symmetrical modeling capabilities
required for balanced three-phase power system analysis.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import CL_BLACK
from pyptp.elements.element_utils import (
    NIL_GUID,
    Guid,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.color_utils import DelphiColor
    from pyptp.network_mv import NetworkMV

    from .presentations import NodePresentation


@dataclass_json
@dataclass
class NodeMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Medium-voltage network node for symmetrical modeling.

    Supports balanced three-phase analysis with comprehensive electrical
    and operational properties for MV distribution system modeling.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for MV nodes."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        short_name: str = string_field()
        id: str = string_field()
        unom: float | int = 0.4
        simultaneity_factor: float = 1.0
        function: str = string_field()
        railtype: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenace_frequency: float = 0.0
        maintenace_duration: float = 0.0
        maintenace_cancel_duration: float = 0.0
        remote_status_indication: bool = False
        gx: float | int = optional_field(0)
        gy: float | int = optional_field(0)
        badly_accessible: bool = False
        ripple_control_frequency: float | int = 0
        ripple_control_voltage: float | int = 0
        ripple_control_angle: float | int = 0
        earthing: bool = False
        re: float = 0.0
        xe: float = 0.0
        no_voltage_check: int = 0
        umin: float = 0.0
        umax: float = 0.0
        d_umax: float = 0.0

        def serialize(self) -> str:
            """Serialize node properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name, skip=""),
                write_quote_string("ShortName", self.short_name, skip=""),
                write_quote_string("ID", self.id, skip=""),
                write_double_no_skip("Unom", self.unom),
                write_double("SimultaneityFactor", self.simultaneity_factor, skip=1.0),
                write_quote_string("Function", self.function, skip=""),
                write_quote_string("Railtype", self.railtype, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration, skip=0.0),
                write_double("MaintenanceFrequency", self.maintenace_frequency, skip=0.0),
                write_double("MaintenanceDuration", self.maintenace_duration, skip=0.0),
                write_double("MaintenanceCancelDuration", self.maintenace_cancel_duration, skip=0.0),
                write_boolean(
                    "RemoteStatusIndication",
                    value=self.remote_status_indication,
                    skip=False,
                ),
                write_double("GX", self.gx, skip=0),
                write_double("GY", self.gy, skip=0),
                write_boolean("BadlyAccessible", value=self.badly_accessible),
                write_double("RippleControlFrequency", self.ripple_control_frequency, skip=0),
                write_double("RippleControlVoltage", self.ripple_control_voltage, skip=0),
                write_double("RippleControlAngle", self.ripple_control_angle, skip=0),
                write_boolean("Earthing", value=self.earthing),
                write_double("Re", self.re, skip=0.0),
                write_double("Xe", self.xe, skip=0.0),
                write_integer("NoVoltageCheck", self.no_voltage_check, skip=0),
                write_double("Umin", self.umin, skip=0.0),
                write_double("Umax", self.umax, skip=0.0),
                write_double("dUmax", self.d_umax, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.General:
            """Parse node properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            guid = data.get("GUID")
            mutation_date = data.get("MutationDate")
            revision_date = data.get("RevisionDate")

            return cls(
                guid=decode_guid(guid) if guid else Guid(uuid4()),
                creation_time=data.get("CreationTime", 0),
                mutation_date=mutation_date if mutation_date is not None else 0,
                revision_date=revision_date if revision_date is not None else 0.0,
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                short_name=data.get("ShortName", ""),
                id=data.get("ID", ""),
                unom=data.get("Unom", 0.4),
                simultaneity_factor=data.get("SimultaneityFactor", 1.0),
                function=data.get("Function", ""),
                railtype=data.get("Railtype", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenace_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenace_duration=data.get("MaintenanceDuration", 0.0),
                maintenace_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                remote_status_indication=data.get("RemoteStatusIndication", False),
                gx=data.get("GX", 0),
                gy=data.get("GY", 0),
                badly_accessible=data.get("BadlyAccessible", False),
                ripple_control_frequency=data.get("RippleControlFrequency", 0),
                ripple_control_voltage=data.get("RippleControlVoltage", 0),
                ripple_control_angle=data.get("RippleControlAngle", 0),
                earthing=data.get("Earthing", False),
                re=data.get("Re", 0.0),
                xe=data.get("Xe", 0.0),
                no_voltage_check=data.get("NoVoltageCheck", 0),
                umin=data.get("Umin", 0.0),
                umax=data.get("Umax", 0.0),
                d_umax=data.get("dUmax", 0.0),
            )

    @dataclass_json
    @dataclass
    class Railtype(DataClassJsonMixin):
        """Electrical properties for node rail/bus configuration."""

        name: str = string_field()
        unom: float = 0.0
        inom: float = 0.0
        ik_dynamic: float = field(default=0.0, metadata=config(field_name="Ik,dynamisch"))
        ik_thermal: float = field(default=0.0, metadata=config(field_name="Ik,thermisch"))
        t_thermal: float = field(default=0.0, metadata=config(field_name="t,thermisch"))

        def serialize(self) -> str:
            """Serialize railtype properties to VNF format."""
            return serialize_properties(
                write_quote_string("Name", self.name, skip=""),
                write_double("Unom", self.unom, skip=0.0),
                write_double("Inom", self.inom, skip=0.0),
                write_double("IkDynamic", self.ik_dynamic, skip=0.0),
                write_double("IkThermal", self.ik_thermal, skip=0.0),
                write_double("Tthermal", self.t_thermal, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.Railtype:
            """Parse railtype properties from VNF data."""
            return cls(
                name=data.get("Name", ""),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("Tthermal", 0.0),
            )

    @dataclass_json
    @dataclass
    class Field(DataClassJsonMixin):
        """Field installation properties for electrical equipment housing."""

        name: str = string_field()
        sort: str = string_field()
        installation_type: int = 0
        conductor_distance: int | float = 0
        electrode_configuration: int = 0
        enclosed_height: float = 0.0
        enclosed_width: float = 0.0
        enclosed_depth: float = 0.0
        to: str = string_field()
        info: str = string_field()

        def serialize(self) -> str:
            """Serialize field properties to VNF format."""
            return serialize_properties(
                write_quote_string("Name", self.name, skip=""),
                write_quote_string("Sort", self.sort, skip=""),
                write_integer("InstallationType", self.installation_type, skip=0),
                write_double("ConductorDistance", self.conductor_distance, skip=0),
                write_integer("ElectrodeConfiguration", self.electrode_configuration, skip=0),
                write_double("EnclosedHeight", self.enclosed_height, skip=0.0),
                write_double("EnclosedWidth", self.enclosed_width, skip=0.0),
                write_double("EnclosedDepth", self.enclosed_depth, skip=0.0),
                write_quote_string("To", self.to, skip=""),
                write_quote_string("Info", self.info, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.Field:
            """Parse field properties from VNF data."""
            return cls(
                name=data.get("Name", ""),
                sort=data.get("Sort", ""),
                installation_type=data.get("InstallationType", 0),
                conductor_distance=data.get("ConductorDistance", 0),
                electrode_configuration=data.get("ElectrodeConfiguration", 0),
                enclosed_height=data.get("EnclosedHeight", 0.0),
                enclosed_width=data.get("EnclosedWidth", 0.0),
                enclosed_depth=data.get("EnclosedDepth", 0.0),
                to=data.get("To", ""),
                info=data.get("Info", ""),
            )

    @dataclass_json
    @dataclass
    class Customer(DataClassJsonMixin):
        """Customer connection and contract information for node."""

        ean: str = string_field()
        name: str = string_field()
        address: str = string_field()
        postal_code: str = string_field()
        city: str = string_field()
        physical_network_area: str = string_field()
        connection_capacity: float = 0.0
        contracted_power: float = 0.0
        contracted_power_returned: float = 0.0
        contract: str = string_field()

        def serialize(self) -> str:
            """Serialize customer properties to VNF format."""
            return serialize_properties(
                write_quote_string("EAN", self.ean, skip=""),
                write_quote_string("Name", self.name, skip=""),
                write_quote_string("Adress", self.address, skip=""),
                write_quote_string("PostalCode", self.postal_code, skip=""),
                write_quote_string("City", self.city, skip=""),
                write_quote_string("PhysicalNetworkArea", self.physical_network_area, skip=""),
                write_double("ConnectionCapacity", self.connection_capacity, skip=0.0),
                write_double("ContractedPower", self.contracted_power, skip=0.0),
                write_double("ContractedPowerReturned", self.contracted_power_returned, skip=0.0),
                write_quote_string("Contract", self.contract, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.Customer:
            """Parse customer properties from VNF data."""
            return cls(
                ean=data.get("EAN", ""),
                name=data.get("Name", ""),
                address=data.get("Adress", ""),
                postal_code=data.get("PostalCode", ""),
                city=data.get("City", ""),
                physical_network_area=data.get("PhysicalNetworkArea", ""),
                connection_capacity=data.get("ConnectionCapacity", 0.0),
                contracted_power=data.get("ContractedPower", 0.0),
                contracted_power_returned=data.get("ContractedPowerReturned", 0.0),
                contract=data.get("Contract", ""),
            )

    @dataclass_json
    @dataclass
    class Installation(DataClassJsonMixin):
        """Physical installation and safety configuration properties."""

        type: int = 0
        earthed: bool = False
        conductor_distance: float = 0.0
        person_distance: float = 0.0
        enclosed: bool = False
        kb: float = 0.0
        kp: float = 0.0
        kp_max: bool = False
        kp_auto: bool = False
        kt: float = 0.0
        electrode_configuration: int = 0
        enclosed_height: float = 0.0
        enclosed_width: float = 0.0
        enclosed_depth: float = 0.0
        light_arc_protection: bool = False

        def serialize(self) -> str:
            """Serialize installation properties to VNF format."""
            return serialize_properties(
                write_integer("Type", self.type, skip=0),
                write_boolean("Earthed", value=self.earthed),
                write_double("ConductorDistance", self.conductor_distance, skip=0.0),
                write_double("PersonDistance", self.person_distance, skip=0.0),
                write_boolean("Enclosed", value=self.enclosed),
                write_double("Kb", self.kb, skip=0.0),
                write_double("Kp", self.kp, skip=0.0),
                write_boolean("KpMax", value=self.kp_max),
                write_boolean("KpAuto", value=self.kp_auto),
                write_double("Kt", self.kt, skip=0.0),
                write_integer("ElectrodeConfiguration", self.electrode_configuration, skip=0),
                write_double("EnclosedHeight", self.enclosed_height, skip=0.0),
                write_double("EnclosedWidth", self.enclosed_width, skip=0.0),
                write_double("EnclosedDepth", self.enclosed_depth, skip=0.0),
                write_boolean("LightArcProtection", value=self.light_arc_protection),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.Installation:
            """Parse installation properties from VNF data."""
            return cls(
                type=data.get("Type", 0),
                earthed=data.get("Earthed", False),
                conductor_distance=data.get("ConductorDistance", 0.0),
                person_distance=data.get("PersonDistance", 0.0),
                enclosed=data.get("Enclosed", False),
                kb=data.get("Kb", 0.0),
                kp=data.get("Kp", 0.0),
                kp_max=data.get("KpMax", False),
                kp_auto=data.get("KpAuto", False),
                kt=data.get("Kt", 0.0),
                electrode_configuration=data.get("ElectrodeConfiguration", 0),
                enclosed_height=data.get("EnclosedHeight", 0.0),
                enclosed_width=data.get("EnclosedWidth", 0.0),
                enclosed_depth=data.get("EnclosedDepth", 0.0),
                light_arc_protection=data.get("LightArcProtection", False),
            )

    @dataclass_json
    @dataclass
    class Icon(DataClassJsonMixin):
        """Visual representation properties for network diagrams."""

        text: str = string_field()
        text_color: DelphiColor = CL_BLACK
        background_color: DelphiColor = CL_BLACK
        shape: int = 0
        size: int = 0

        def serialize(self) -> str:
            """Serialize icon properties to VNF format."""
            return serialize_properties(
                write_quote_string("Text", self.text, skip=""),
                write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
                write_delphi_color("BackgroundColor", self.background_color, skip=CL_BLACK),
                write_integer("Shape", self.shape, skip=0),
                write_integer("Size", self.size, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.Icon:
            """Parse icon properties from VNF data."""
            return cls(
                text=data.get("Text", ""),
                text_color=data.get("TextColor", CL_BLACK),
                background_color=data.get("BackgroundColor", CL_BLACK),
                shape=data.get("Shape", 0),
                size=data.get("Size", 0),
            )

    @dataclass_json
    @dataclass
    class DifferentialProtection(DataClassJsonMixin):
        """Differential protection settings for node."""

        present: bool = False
        type_name: str = string_field()
        t_input: float = 0.0
        t_output: float = 0.0
        setting_sort: int = 0
        dIg: float = dataclasses.field(default=0.0, metadata=config(field_name="dI>"))  # noqa: N815
        tg: float = dataclasses.field(default=0.0, metadata=config(field_name="t>"))
        dIgg: float = dataclasses.field(default=0.0, metadata=config(field_name="dI>>"))  # noqa: N815
        tgg: float = dataclasses.field(default=0.0, metadata=config(field_name="t>>"))
        m: float = 0.0
        dId: float = 0.0  # noqa: N815
        k1: float = 0.0
        k2: float = 0.0

        def serialize(self) -> str:
            """Serialize differential protection properties to VNF format."""
            return serialize_properties(
                write_quote_string("TypeName", self.type_name, skip=""),
                write_double("Tinput", self.t_input, skip=0.0),
                write_double("Toutput", self.t_output, skip=0.0),
                write_integer("SettingSort", self.setting_sort, skip=0),
                write_double("dI>", self.dIg, skip=0.0),
                write_double("t>", self.tg, skip=0.0),
                write_double("dI>>", self.dIgg, skip=0.0),
                write_double("t>>", self.tgg, skip=0.0),
                write_double("m", self.m, skip=0.0),
                write_double("dId", self.dId, skip=0.0),
                write_double("k1", self.k1, skip=0.0),
                write_double("k2", self.k2, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.DifferentialProtection:
            """Parse differential protection properties from VNF data."""
            return cls(
                present=True,
                type_name=data.get("TypeName", ""),
                t_input=data.get("Tinput", 0.0),
                t_output=data.get("Toutput", 0.0),
                setting_sort=data.get("SettingSort", 0),
                dIg=data.get("dI>", 0.0),
                tg=data.get("t>", 0.0),
                dIgg=data.get("dI>>", 0.0),
                tgg=data.get("t>>", 0.0),
                m=data.get("m", 0.0),
                dId=data.get("dId", 0.0),
                k1=data.get("k1", 0.0),
                k2=data.get("k2", 0.0),
            )

    @dataclass_json
    @dataclass
    class DifferentialProtectionSwitch(DataClassJsonMixin):
        """Switch reference for differential protection system."""

        switch: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize differential protection switch properties to VNF format."""
            from pyptp.elements.serialization_helpers import write_guid

            return serialize_properties(
                write_guid("Switch", self.switch),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.DifferentialProtectionSwitch:
            """Parse differential protection switch properties from VNF data."""
            return cls(
                switch=decode_guid(data.get("Switch", str(NIL_GUID))),
            )

    @dataclass_json
    @dataclass
    class DifferentialProtectionTransferTripSwitch(DataClassJsonMixin):
        """Transfer trip switch reference for differential protection."""

        transfer_circuit_breaker: Guid = field(
            default=NIL_GUID,
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )

        def serialize(self) -> str:
            """Serialize transfer trip switch properties to VNF format."""
            from pyptp.elements.serialization_helpers import write_guid

            return serialize_properties(
                write_guid("TransferCircuitBreaker", self.transfer_circuit_breaker),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeMV.DifferentialProtectionTransferTripSwitch:
            """Parse transfer trip switch properties from VNF data."""
            return cls(
                transfer_circuit_breaker=decode_guid(data.get("TransferCircuitBreaker", str(NIL_GUID))),
            )

    general: General
    presentations: list[NodePresentation]
    railtype: Railtype | None = None
    fields: list[Field] | None = None
    customer: Customer | None = None
    installation: Installation | None = None
    icon: Icon | None = None
    differential_protection: DifferentialProtection | None = None
    differential_protection_switches: list[DifferentialProtectionSwitch] = field(default_factory=list)
    differential_protection_transfer_trip_switch: DifferentialProtectionTransferTripSwitch | None = None

    def register(self, network: NetworkMV) -> None:
        """Register node in MV network with GUID-based indexing.

        Args:
            network: Target MV network for node registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.nodes:
            logger.critical("Node %s already exists, overwriting", self.general.guid)
        network.nodes[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the node to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []

        lines.append(f"#General {self.general.serialize()}")

        if self.railtype is not None:
            lines.append(f"#Railtype {self.railtype.serialize()}")

        if self.fields is not None:
            lines.extend(f"#Field {field.serialize()}" for field in self.fields)

        if self.customer is not None:
            lines.append(f"#Customer {self.customer.serialize()}")

        if self.installation is not None:
            lines.append(f"#Installation {self.installation.serialize()}")

        if self.icon is not None:
            lines.append(f"#Icon {self.icon.serialize()}")

        if self.differential_protection is not None and self.differential_protection.present:
            lines.append(f"#DifferentialProtection {self.differential_protection.serialize()}")

            lines.extend(
                f"#DifferentialProtectionSwitch {differential_switch.serialize()}"
                for differential_switch in self.differential_protection_switches
            )

            if self.differential_protection_transfer_trip_switch is not None:
                serialized_transfer = self.differential_protection_transfer_trip_switch.serialize()
                lines.append(f"#DifferentialProtectionTransferTripSwitch {serialized_transfer}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        if self.notes:
            lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> NodeMV:
        """Parse node from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data.

        Returns:
            Initialized TNodeMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from pyptp.elements.mv.presentations import NodePresentation

            presentation = NodePresentation.deserialize(pres_data)
            presentations.append(presentation)

        # Parse installation section
        installation = None
        installation_data = data.get("installation", [{}])[0] if data.get("installation") else None
        if installation_data:
            installation = cls.Installation.deserialize(installation_data)

        # Parse railtype section
        railtype = None
        railtype_data = data.get("railtype", [{}])[0] if data.get("railtype") else None
        if railtype_data:
            railtype = cls.Railtype.deserialize(railtype_data)

        return cls(
            general=general,
            presentations=presentations,
            installation=installation,
            railtype=railtype,
        )
