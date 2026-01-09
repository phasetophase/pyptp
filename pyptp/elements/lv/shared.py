"""Shared data types for LV network element modeling.

Provides common structures for cable specifications, efficiency curves,
control systems, and other reusable components across multiple LV
network elements with complex electrical characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    FloatCoords,
    decode_float_coords,
    encode_float_coords,
    encode_string,
    optional_field,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_double_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
)


@dataclass_json
@dataclass
class CableType(DataClassJsonMixin):
    """Electrical and thermal characteristics for LV cable types.

    Defines comprehensive cable parameters including impedance,
    current capacity, thermal limits, and frequency response
    for accurate asymmetrical load flow modeling.
    """

    short_name: str = field(metadata=config(encoder=encode_string))
    unom: float | int = optional_field(0)
    price: float = 0
    C: float = optional_field(0)
    C0: float = optional_field(0)
    Inom0: int = optional_field(0)
    G1: float = optional_field(0)
    Inom1: int = optional_field(0)
    G2: float = optional_field(0)
    Inom2: int = optional_field(0)
    G3: float = optional_field(0)
    Inom3: int = optional_field(0)
    Ik1s: float = optional_field(0)
    TR: int = optional_field(0)
    TInom: int | float = optional_field(0)
    TIk1s: int | float = optional_field(0)
    frequency: int | float = optional_field(0)
    R_c: int | float = optional_field(0)
    X_c: int | float = optional_field(0)
    R_cc_n: int | float = optional_field(0)
    X_cc_n: int | float = optional_field(0)
    R_cc_o: int | float = optional_field(0)
    X_cc_o: int | float = optional_field(0)
    R_e: int | float = optional_field(0)
    X_e: int | float = optional_field(0)
    R_ce: int | float = optional_field(0)
    X_ce: int | float = optional_field(0)
    R_h: int | float = optional_field(0)
    X_h: int | float = optional_field(0)
    R_ch_n: int | float = optional_field(0)
    X_ch_n: int | float = optional_field(0)
    R_ch_o: int | float = optional_field(0)
    X_ch_o: int | float = optional_field(0)
    R_hh_n: int | float = optional_field(0)
    X_hh_n: int | float = optional_field(0)
    R_hh_o: int | float = optional_field(0)
    X_hh_o: int | float = optional_field(0)
    R_he: int | float = optional_field(0)
    X_he: int | float = optional_field(0)
    Inom_e: int | float = optional_field(0)
    Ik1s_e: int | float = optional_field(0)
    Inom_h: int | float = optional_field(0)
    Ik1s_h: int | float = optional_field(0)
    R_cR_n: float = field(default=1.0, metadata=config(field_name="R_c/R_n"))

    def serialize(self) -> str:
        """Serialize CableType properties to a string."""
        return serialize_properties(
            write_quote_string("ShortName", self.short_name),
            write_double("Unom", self.unom, 0),
            write_double_no_skip("Price", self.price),
            write_double("C", self.C, 0),
            write_double("C0", self.C0, 0),
            write_integer("Inom0", self.Inom0, 0),
            write_double("G1", self.G1, 0),
            write_integer("Inom1", self.Inom1, 0),
            write_double("G2", self.G2, 0),
            write_integer("Inom2", self.Inom2, 0),
            write_double("G3", self.G3, 0),
            write_integer("Inom3", self.Inom3, 0),
            write_double("Ik1s", self.Ik1s, 0),
            write_integer_no_skip("TR", self.TR),
            write_double("TInom", self.TInom, 0),
            write_double("TIk1s", self.TIk1s, 0),
            write_double("Frequency", self.frequency, 0),
            write_double("R_c", self.R_c, 0),
            write_double("X_c", self.X_c, 0),
            write_double("R_cc_n", self.R_cc_n, 0),
            write_double("X_cc_n", self.X_cc_n, 0),
            write_double("R_cc_o", self.R_cc_o, 0),
            write_double("X_cc_o", self.X_cc_o, 0),
            write_double("R_e", self.R_e, 0),
            write_double("X_e", self.X_e, 0),
            write_double("R_ce", self.R_ce, 0),
            write_double("X_ce", self.X_ce, 0),
            write_double("R_h", self.R_h, 0),
            write_double("X_h", self.X_h, 0),
            write_double("R_ch_n", self.R_ch_n, 0),
            write_double("X_ch_n", self.X_ch_n, 0),
            write_double("R_ch_o", self.R_ch_o, 0),
            write_double("X_ch_o", self.X_ch_o, 0),
            write_double("R_hh_n", self.R_hh_n, 0),
            write_double("X_hh_n", self.X_hh_n, 0),
            write_double("R_hh_o", self.R_hh_o, 0),
            write_double("X_hh_o", self.X_hh_o, 0),
            write_double("R_he", self.R_he, 0),
            write_double("X_he", self.X_he, 0),
            write_double("Inom_e", self.Inom_e, 0),
            write_double("Ik1s_e", self.Ik1s_e, 0),
            write_double("Inom_h", self.Inom_h, 0),
            write_double("Ik1s_h", self.Ik1s_h, 0),
            write_double("R_c/R_n", self.R_cR_n, 1.0),
        )

    @classmethod
    def deserialize(cls, data: dict) -> CableType:
        """Deserialize CableType from a dictionary."""
        return cls(
            short_name=data.get("ShortName", ""),
            unom=data.get("Unom", 0),
            price=data.get("Price", 0),
            C=data.get("C", 0),
            C0=data.get("C0", 0),
            Inom0=data.get("Inom0", 0),
            G1=data.get("G1", 0),
            Inom1=data.get("Inom1", 0),
            G2=data.get("G2", 0),
            Inom2=data.get("Inom2", 0),
            G3=data.get("G3", 0),
            Inom3=data.get("Inom3", 0),
            Ik1s=data.get("Ik1s", 0),
            TR=data.get("TR", 0),
            TInom=data.get("TInom", 0),
            TIk1s=data.get("TIk1s", 0),
            frequency=data.get("Frequency", 0),
            R_c=data.get("R_c", 0),
            X_c=data.get("X_c", 0),
            R_cc_n=data.get("R_cc_n", 0),
            X_cc_n=data.get("X_cc_n", 0),
            R_cc_o=data.get("R_cc_o", 0),
            X_cc_o=data.get("X_cc_o", 0),
            R_e=data.get("R_e", 0),
            X_e=data.get("X_e", 0),
            R_ce=data.get("R_ce", 0),
            X_ce=data.get("X_ce", 0),
            R_h=data.get("R_h", 0),
            X_h=data.get("X_h", 0),
            R_ch_n=data.get("R_ch_n", 0),
            X_ch_n=data.get("X_ch_n", 0),
            R_ch_o=data.get("R_ch_o", 0),
            X_ch_o=data.get("X_ch_o", 0),
            R_hh_n=data.get("R_hh_n", 0),
            X_hh_n=data.get("X_hh_n", 0),
            R_hh_o=data.get("R_hh_o", 0),
            X_hh_o=data.get("X_hh_o", 0),
            R_he=data.get("R_he", 0),
            X_he=data.get("X_he", 0),
            Inom_e=data.get("Inom_e", 0),
            Ik1s_e=data.get("Ik1s_e", 0),
            Inom_h=data.get("Inom_h", 0),
            Ik1s_h=data.get("Ik1s_h", 0),
            R_cR_n=data.get("R_c/R_n", 1.0),
        )


@dataclass_json
@dataclass
class FuseType(DataClassJsonMixin):
    """Electrotechnical properties of a fuse."""

    short_name: str = string_field()
    unom: float = 0
    inom: float = 0
    I: list[float] = field(default_factory=lambda: [0] * 16)  # noqa: E741
    T: list[float] = field(default_factory=lambda: [0] * 16)

    def __post_init__(self) -> None:
        """Properly read the I and T objects into the Fuse."""
        if isinstance(self.I, dict):
            self.I = [self.I.get(f"I{i + 1}", 0) for i in range(16)]
        if isinstance(self.T, dict):
            self.T = [self.T.get(f"T{i + 1}", 0) for i in range(16)]

    def serialize(self) -> str:
        """Serialize FuseType properties to a string."""
        props = [
            write_quote_string("ShortName", self.short_name),
            write_double("Unom", self.unom),
            write_double("Inom", self.inom),
        ]
        for i in range(16):
            # Don't convert to int - preserve decimal values
            props.append(write_double(f"I{i + 1}", self.I[i]))
            # Use no_skip for T values to preserve even 0.0 values
            props.append(write_double_no_skip(f"T{i + 1}", self.T[i]))
        return " ".join(p for p in props if p) + " "

    @classmethod
    def deserialize(cls, data: dict) -> FuseType:
        """Deserialize FuseType from dictionary, handling I1-I16 and T1-T16 fields."""
        # Create a copy to avoid modifying the original data
        processed_data = data.copy()

        # Convert I1-I16 fields to I list
        i_values = []
        for i in range(1, 17):
            key = f"I{i}"
            if key in processed_data:
                i_values.append(processed_data.pop(key))
            else:
                i_values.append(0)

        # Convert T1-T16 fields to T list
        t_values = []
        for i in range(1, 17):
            key = f"T{i}"
            if key in processed_data:
                t_values.append(processed_data.pop(key))
            else:
                t_values.append(0)

        # Add the converted lists to the data
        processed_data["I"] = i_values
        processed_data["T"] = t_values

        return cls(
            short_name=processed_data.get("ShortName", ""),
            unom=processed_data.get("Unom", 0),
            inom=processed_data.get("Inom", 0),
            I=i_values,
            T=t_values,
        )


@dataclass_json
@dataclass
class CurrentType(DataClassJsonMixin):
    """Current type."""

    short_name: str = string_field()
    inom: float | int = 0
    setting_sort: int = 0

    I: list[int] | None = field(default_factory=lambda: [0] * 12)  # noqa: E741
    T: list[int] | None = field(default_factory=lambda: [0] * 12)

    I_great: float | int | None = field(default=0, metadata=config(field_name="I>"))
    T_great: float | int | None = field(default=0, metadata=config(field_name="T>"))

    I_greater: float | int | None = field(default=0, metadata=config(field_name="I>>"))
    T_greater: float | int | None = field(default=0, metadata=config(field_name="T>>"))

    I_greatest: float | int | None = field(default=0, metadata=config(field_name="I>>>"))
    T_greatest: float | int | None = field(default=0, metadata=config(field_name="T>>>"))

    M: float | int | None = 0
    Id: float | int | None = 0

    alpha: float | int | None = 0
    beta: float | int | None = 0
    c: float | int | None = 0
    d: float | int | None = 0
    e: float | int | None = 0
    ilt: float | int | None = 0
    ist: float | int | None = 0

    def serialize(self) -> str:
        """Serialize CurrentType properties to a string."""
        props = [
            write_quote_string("ShortName", self.short_name),
            write_double("Inom", self.inom),
            write_integer("SettingSoort", int(self.setting_sort)),
            write_double("I>", self.I_great if self.I_great is not None else 0),
            write_double("T>", self.T_great if self.T_great is not None else 0),
            write_double("I>>", self.I_greater if self.I_greater is not None else 0),
            write_double("T>>", self.T_greater if self.T_greater is not None else 0),
            write_double("I>>>", self.I_greatest if self.I_greatest is not None else 0),
            write_double("T>>>", self.T_greatest if self.T_greatest is not None else 0),
            write_double("M", self.M if self.M is not None else 0),
            write_double("Id", self.Id if self.Id is not None else 0),
            write_double("Alpha", self.alpha if self.alpha is not None else 0),
            write_double("Beta", self.beta if self.beta is not None else 0),
            write_double("c", self.c if self.c is not None else 0),
            write_double("d", self.d if self.d is not None else 0),
            write_double("e", self.e if self.e is not None else 0),
            write_double("Ilt", self.ilt if self.ilt is not None else 0),
            write_double("Ist", self.ist if self.ist is not None else 0),
        ]
        if self.I is not None:
            for idx, val in enumerate(self.I, start=1):
                props.append(write_integer(f"I{idx}", int(val)))
        if self.T is not None:
            for idx, val in enumerate(self.T, start=1):
                props.append(write_integer(f"T{idx}", int(val)))
        return " ".join(p for p in props if p) + " "

    @classmethod
    def deserialize(cls, data: dict) -> CurrentType:
        """Deserialize CurrentType from a dictionary."""
        # Handle I and T list conversion
        i_values = data.get("I", [0] * 12)
        t_values = data.get("T", [0] * 12)

        # If I and T are provided as individual I1-I12, T1-T12 keys, convert them
        if "I1" in data:
            i_values = []
            for i in range(1, 13):
                i_values.append(data.get(f"I{i}", 0))

        if "T1" in data:
            t_values = []
            for i in range(1, 13):
                t_values.append(data.get(f"T{i}", 0))

        return cls(
            short_name=data.get("ShortName", ""),
            inom=data.get("Inom", 0),
            setting_sort=data.get("SettingSoort", 0),
            I=i_values,
            T=t_values,
            I_great=data.get("I>", 0),
            T_great=data.get("T>", 0),
            I_greater=data.get("I>>", 0),
            T_greater=data.get("T>>", 0),
            I_greatest=data.get("I>>>", 0),
            T_greatest=data.get("T>>>", 0),
            M=data.get("M", 0),
            Id=data.get("Id", 0),
            alpha=data.get("Alpha", 0),
            beta=data.get("Beta", 0),
            c=data.get("c", 0),
            d=data.get("d", 0),
            e=data.get("e", 0),
            ilt=data.get("Ilt", 0),
            ist=data.get("Ist", 0),
        )


@dataclass_json
@dataclass
class GeoCablePart(DataClassJsonMixin):
    """Geographical information of a cable part."""

    coordinates: FloatCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
    )

    def serialize(self) -> str:
        """Serialize GeoCablePart coordinates to a string."""
        props = []
        if self.coordinates:
            props.append(f"Coordinates:{encode_float_coords(self.coordinates)}")
        return " ".join(props) + " "

    @classmethod
    def deserialize(cls, data: dict) -> GeoCablePart:
        """Deserialize GeoCablePart from a dictionary."""
        coordinates = data.get("Coordinates", [])
        if isinstance(coordinates, str):
            coordinates = decode_float_coords(coordinates)
        return cls(
            coordinates=coordinates,
        )


@dataclass_json
@dataclass
class Text(DataClassJsonMixin):
    """Represent a single free-text note."""

    text: str = string_field()

    def encode(self) -> dict[str, Any]:
        """Format Note as a 'Text':'text' mapping."""
        return {"Text": self.text}

    @classmethod
    def deserialize(cls, data: dict) -> Text:
        """Deserialize Text from a dictionary."""
        return cls(
            text=data.get("text", data.get("Text", "")),
        )


@dataclass_json
@dataclass
class EfficiencyType(DataClassJsonMixin):
    """Efficiency Type."""

    input1: float = 0.0
    output1: float = 0.0
    input2: float = 0.0
    output2: float = 0.0
    input3: float = 0.0
    output3: float = 0.0
    input4: float = 0.0
    output4: float = 0.0
    input5: float = 0.0
    output5: float = 0.0

    def serialize(self) -> str:
        """Serialize EfficiencyType properties to a string."""
        props = []
        for i in range(1, 6):
            props.append(f"Input{i}:{getattr(self, f'input{i}')}")
            props.append(f"Output{i}:{getattr(self, f'output{i}')}")
        return " ".join(props) + " "

    @classmethod
    def deserialize(cls, data: dict) -> EfficiencyType:
        """Deserialize EfficiencyType from a dictionary."""
        return cls(
            input1=data.get("Input1", 0.0),
            output1=data.get("Output1", 0.0),
            input2=data.get("Input2", 0.0),
            output2=data.get("Output2", 0.0),
            input3=data.get("Input3", 0.0),
            output3=data.get("Output3", 0.0),
            input4=data.get("Input4", 0.0),
            output4=data.get("Output4", 0.0),
            input5=data.get("Input5", 0.0),
            output5=data.get("Output5", 0.0),
        )


@dataclass_json
@dataclass
class Fields(DataClassJsonMixin):
    """Field information."""

    values: list

    def serialize(self) -> str:
        """Serialize Fields values to a string."""
        props = []
        for i, v in enumerate(self.values):
            props.append(f"Name{i}:'{v}'")
        return " ".join(props)

    @classmethod
    def deserialize(cls, data: dict) -> Fields:
        """Deserialize Fields from a dictionary."""
        # Handle different ways values might be provided
        values = data.get("values", [])
        if not values:
            # If values are provided as Name0, Name1, etc., convert them
            values = []
            i = 0
            while f"Name{i}" in data:
                values.append(data[f"Name{i}"])
                i += 1
        return cls(
            values=values,
        )


@dataclass_json
@dataclass
class Comment(DataClassJsonMixin):
    """Comment."""

    text: str = string_field()

    def serialize(self) -> str:
        """Serialize Comment text to a string."""
        return f"Text:{self.text}"

    @classmethod
    def deserialize(cls, data: dict) -> Comment:
        """Deserialize Comment from a dictionary."""
        return cls(
            text=data.get("text", data.get("Text", "")),
        )


@dataclass_json
@dataclass
class PControl(DataClassJsonMixin):
    """Power Control."""

    sort: int = 0

    start_time1: float = 0.0
    end_time1: float = 0.0
    input1: float = 0.0
    output1: float = 0.0

    start_time2: float = 0.0
    end_time2: float = 0.0
    input2: float = 0.0
    output2: float = 0.0

    start_time3: float = 0.0
    end_time3: float = 0.0
    input3: float = 0.0
    output3: float = 0.0

    start_time4: float = 0.0
    end_time4: float = 0.0
    input4: float = 0.0
    output4: float = 0.0

    start_time5: float = 0.0
    end_time5: float = 0.0
    input5: float = 0.0
    output5: float = 0.0

    measure_field: str = string_field()

    def serialize(self) -> str:
        """Serialize PControl properties to a string."""
        props = []
        props.append(f"Sort:{self.sort}")
        for i in range(1, 6):
            props.append(f"StartTime{i}:{getattr(self, f'start_time{i}')}")
            props.append(f"EndTime{i}:{getattr(self, f'end_time{i}')}")
            props.append(f"Input{i}:{getattr(self, f'input{i}')}")
            props.append(f"Output{i}:{getattr(self, f'output{i}')}")
        props.append(f"MeasureField:'{self.measure_field}'")
        return " ".join(props)

    @classmethod
    def deserialize(cls, data: dict) -> PControl:
        """Deserialize PControl from a dictionary."""
        return cls(
            sort=data.get("Sort", 0),
            start_time1=data.get("StartTime1", 0.0),
            end_time1=data.get("EndTime1", 0.0),
            input1=data.get("Input1", 0.0),
            output1=data.get("Output1", 0.0),
            start_time2=data.get("StartTime2", 0.0),
            end_time2=data.get("EndTime2", 0.0),
            input2=data.get("Input2", 0.0),
            output2=data.get("Output2", 0.0),
            start_time3=data.get("StartTime3", 0.0),
            end_time3=data.get("EndTime3", 0.0),
            input3=data.get("Input3", 0.0),
            output3=data.get("Output3", 0.0),
            start_time4=data.get("StartTime4", 0.0),
            end_time4=data.get("EndTime4", 0.0),
            input4=data.get("Input4", 0.0),
            output4=data.get("Output4", 0.0),
            start_time5=data.get("StartTime5", 0.0),
            end_time5=data.get("EndTime5", 0.0),
            input5=data.get("Input5", 0.0),
            output5=data.get("Output5", 0.0),
            measure_field=data.get("MeasureField", ""),
        )


@dataclass_json
@dataclass
class HarmonicsType(DataClassJsonMixin):
    """Shared Harmonics type for LV and MV elements."""

    h: list[float] | None = field(default_factory=lambda: [0] * 99)
    angle: list[float] | None = field(default_factory=lambda: [0] * 99)

    def serialize(self) -> str:
        """Serialize HarmonicsType properties to a string."""
        props = []
        if self.h is not None:
            for i, value in enumerate(self.h, start=1):
                if value != 0:
                    props.append(f"h{i}:{value}")
        if self.angle is not None:
            for i, value in enumerate(self.angle, start=1):
                if value != 0:
                    props.append(f"Angle{i}:{value}")
        return " ".join(props) + " "

    @classmethod
    def deserialize(cls, data: dict) -> HarmonicsType:
        """Deserialize HarmonicsType from a dictionary."""
        # Handle h and Angle list conversion
        h_values = [0.0] * 99
        angle_values = [0.0] * 99

        # Check for any h{i} or Angle{i} keys in the data
        has_h_keys = any(key.startswith("h") and key[1:].isdigit() for key in data)
        has_angle_keys = any(key.startswith("Angle") and key[5:].isdigit() for key in data)

        if has_h_keys:
            for i in range(1, 100):
                if f"h{i}" in data:
                    h_values[i - 1] = data[f"h{i}"]

        if has_angle_keys:
            for i in range(1, 100):
                if f"Angle{i}" in data:
                    angle_values[i - 1] = data[f"Angle{i}"]

        # If no individual keys found, use the provided lists
        if not has_h_keys:
            h_values = data.get("h", [0] * 99)
        if not has_angle_keys:
            angle_values = data.get("Angle", [0] * 99)

        return cls(
            h=h_values,
            angle=angle_values,
        )
