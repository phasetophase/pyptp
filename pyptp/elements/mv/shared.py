"""Shared Types."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    FloatCoords,
    decode_float_coords,
    encode_float_coords,
    optional_field,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
)


@dataclass_json
@dataclass
class CableType(DataClassJsonMixin):
    """Cable type."""

    short_name: str = string_field()
    info: str = string_field()
    unom: float | int = optional_field(0)
    price: float | int = 0.0
    r: float = optional_field(0)
    x: float = optional_field(0)
    c: float = optional_field(0)
    c0: float = optional_field(0)
    tan_delta: float = optional_field(0)
    r0: float = optional_field(0)
    x0: float = optional_field(0)
    inom0: float = optional_field(0)
    g1: int | float = 0.0
    inom1: int | float = 0.0
    g2: int | float = 0.0
    inom2: int | float = 0.0
    g3: int | float = 0
    inom3: int | float = 0.0
    ik1s: int | float = 0.0
    tr: int | float = 0.0
    TInom: int | float = 0.0
    TIk1s: int | float = 0.0
    frequency: int | float = 0
    pulse_velocity: int | float = optional_field(0)

    def serialize(self) -> str:
        """Serialize CableType properties."""
        return serialize_properties(
            write_quote_string_no_skip("ShortName", self.short_name),
            write_quote_string("Info", self.info),
            write_double("Unom", self.unom, skip=0),
            write_double("Price", self.price),
            write_double("R", self.r, skip=0),
            write_double("X", self.x, skip=0),
            write_double("C", self.c, skip=0),
            write_double("C0", self.c0, skip=0),
            write_double("TanDelta", self.tan_delta, skip=0),
            write_double("R0", self.r0, skip=0),
            write_double("X0", self.x0, skip=0),
            write_double_no_skip("Inom0", self.inom0),
            write_double_no_skip("G1", self.g1),
            write_double_no_skip("Inom1", self.inom1),
            write_double_no_skip("G2", self.g2),
            write_double_no_skip("Inom2", self.inom2),
            write_double_no_skip("G3", self.g3),
            write_double_no_skip("Inom3", self.inom3),
            write_double("Ik1s", self.ik1s),
            write_double("TR", self.tr),
            write_double("TInom", self.TInom),
            write_double("TIk1s", self.TIk1s),
            write_double("Frequency", self.frequency),
            write_double("PulseVelocity", self.pulse_velocity, skip=0),
        )

    @classmethod
    def deserialize(cls, data: dict) -> CableType:
        """Deserialize CableType properties."""
        return cls(
            short_name=data.get("ShortName", ""),
            info=data.get("Info", ""),
            unom=data.get("Unom", 0),
            price=data.get("Price", 0.0),
            r=data.get("R", 0),
            x=data.get("X", 0),
            c=data.get("C", 0),
            c0=data.get("C0", 0),
            tan_delta=data.get("TanDelta", 0),
            r0=data.get("R0", 0),
            x0=data.get("X0", 0),
            inom0=data.get("Inom0", 0),
            g1=data.get("G1", 0.0),
            inom1=data.get("Inom1", 0.0),
            g2=data.get("G2", 0.0),
            inom2=data.get("Inom2", 0.0),
            g3=data.get("G3", 0),
            inom3=data.get("Inom3", 0.0),
            ik1s=data.get("Ik1s", 0.0),
            tr=data.get("TR", 0.0),
            TInom=data.get("TInom", 0.0),
            TIk1s=data.get("TIk1s", 0.0),
            frequency=data.get("Frequency", 0),
            pulse_velocity=data.get("PulseVelocity", 0),
        )


@dataclass_json
@dataclass
class Text(DataClassJsonMixin):
    """Represent a single free-text note."""

    text: str = string_field()
    """Text content of the note."""

    def serialize(self) -> str:
        """Serialize Text properties."""
        return serialize_properties(write_quote_string_no_skip("Text", self.text))

    @classmethod
    def deserialize(cls, data: dict) -> Text:
        """Deserialize Text properties."""
        return cls(text=data.get("Text", ""))

    def encode(self) -> dict[str, Any]:
        """Format Note as a 'Text':'text' mapping."""
        return {"Text": self.text}


@dataclass_json
@dataclass
class FuseType(DataClassJsonMixin):
    """Fuse Type."""

    short_name: str = string_field()
    unom: int | float = 0
    inom: int | float = 0
    I: list[int] | None = field(default_factory=lambda: [0] * 16)  # noqa: E741
    T: list[int] | None = field(default_factory=lambda: [0] * 16)

    def serialize(self) -> str:
        """Serialize FuseType properties."""
        props = [
            write_quote_string_no_skip("ShortName", self.short_name),
            write_double_no_skip("Unom", self.unom),
            write_double_no_skip("Inom", self.inom),
        ]
        if self.I:
            props.extend([write_double_no_skip(f"I{i + 1}", val) for i, val in enumerate(self.I)])
        if self.T:
            props.extend([write_double_no_skip(f"T{i + 1}", val) for i, val in enumerate(self.T)])
        return serialize_properties(*props)

    @classmethod
    def deserialize(cls, data: dict) -> FuseType:
        """Deserialize FuseType properties."""
        i_values = []
        t_values = []

        for i in range(1, 17):
            if f"I{i}" in data:
                i_values.append(data[f"I{i}"])
            if f"T{i}" in data:
                t_values.append(data[f"T{i}"])

        return cls(
            short_name=data.get("ShortName", ""),
            unom=data.get("Unom", 0),
            inom=data.get("Inom", 0),
            I=i_values if i_values else None,
            T=t_values if t_values else None,
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
    t_great: float | int | None = field(default=0, metadata=config(field_name="T>"))

    I_greater: float | int | None = field(default=0, metadata=config(field_name="I>>"))
    t_greater: float | int | None = field(default=0, metadata=config(field_name="T>>"))

    I_greatest: float | int | None = field(default=0, metadata=config(field_name="I>>>"))
    t_greatest: float | int | None = field(default=0, metadata=config(field_name="T>>>"))

    M: float | int | None = 0
    Id: float | int | None = 0

    alpha: float | int | None = 0
    beta: float | int | None = 0
    c: float | int | None = 0
    d: float | int | None = 0
    e: float | int | None = 0
    Ilt: float | int | None = 0
    Ist: float | int | None = 0

    def serialize(self) -> str:
        """Serialize CurrentType properties."""
        props = [
            write_quote_string_no_skip("ShortName", self.short_name),
            write_double_no_skip("Inom", self.inom),
            write_integer_no_skip("SettingSoort", self.setting_sort),
        ]
        if self.I:
            props.extend([write_double_no_skip(f"I{i + 1}", val) for i, val in enumerate(self.I)])
        if self.T:
            props.extend([write_double_no_skip(f"T{i + 1}", val) for i, val in enumerate(self.T)])
        if self.I_great is not None and self.I_great != 0:
            props.append(write_double_no_skip("I>", self.I_great))
        if self.t_great is not None and self.t_great != 0:
            props.append(write_double_no_skip("T>", self.t_great))
        if self.I_greater is not None and self.I_greater != 0:
            props.append(write_double_no_skip("I>>", self.I_greater))
        if self.t_greater is not None and self.t_greater != 0:
            props.append(write_double_no_skip("T>>", self.t_greater))
        if self.I_greatest is not None and self.I_greatest != 0:
            props.append(write_double_no_skip("I>>>", self.I_greatest))
        if self.t_greatest is not None and self.t_greatest != 0:
            props.append(write_double_no_skip("T>>>", self.t_greatest))
        if self.M is not None and self.M != 0:
            props.append(write_double_no_skip("M", self.M))
        if self.Id is not None and self.Id != 0:
            props.append(write_double_no_skip("Id", self.Id))
        if self.alpha is not None and self.alpha != 0:
            props.append(write_double_no_skip("Alpha", self.alpha))
        if self.beta is not None and self.beta != 0:
            props.append(write_double_no_skip("Beta", self.beta))
        if self.c is not None and self.c != 0:
            props.append(write_double_no_skip("c", self.c))
        if self.d is not None and self.d != 0:
            props.append(write_double_no_skip("d", self.d))
        if self.e is not None and self.e != 0:
            props.append(write_double_no_skip("e", self.e))
        if self.Ilt is not None and self.Ilt != 0:
            props.append(write_double_no_skip("Ilt", self.Ilt))
        if self.Ist is not None and self.Ist != 0:
            props.append(write_double_no_skip("Ist", self.Ist))
        return serialize_properties(*props)

    @classmethod
    def deserialize(cls, data: dict) -> CurrentType:
        """Deserialize CurrentType properties."""
        i_values = []
        t_values = []

        for i in range(1, 13):
            if f"I{i}" in data:
                i_values.append(data[f"I{i}"])
            if f"T{i}" in data:
                t_values.append(data[f"T{i}"])

        return cls(
            short_name=data.get("ShortName", ""),
            inom=data.get("Inom", 0),
            setting_sort=data.get("SettingSoort", 0),
            I=i_values if i_values else None,
            T=t_values if t_values else None,
            I_great=data.get("I>", 0),
            t_great=data.get("T>", 0),
            I_greater=data.get("I>>", 0),
            t_greater=data.get("T>>", 0),
            I_greatest=data.get("I>>>", 0),
            t_greatest=data.get("T>>>", 0),
            M=data.get("M", 0),
            Id=data.get("Id", 0),
            alpha=data.get("Alpha", 0),
            beta=data.get("Beta", 0),
            c=data.get("c", 0),
            d=data.get("d", 0),
            e=data.get("e", 0),
            Ilt=data.get("Ilt", 0),
            Ist=data.get("Ist", 0),
        )


@dataclass_json
@dataclass
class GeoCablePart(DataClassJsonMixin):
    """Geography of the cable parts."""

    coordinates: FloatCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
    )

    def serialize(self) -> str:
        """Serialize GeoCablePart properties."""
        props = []
        if self.coordinates:
            props.append(f"Coordinates:{encode_float_coords(self.coordinates)}")
        return " ".join(props)

    @classmethod
    def deserialize(cls, data: dict) -> GeoCablePart:
        """Deserialize GeoCablePart properties."""
        return cls(
            coordinates=decode_float_coords(data.get("Coordinates", "''")),
        )


@dataclass_json
@dataclass
class Fields(DataClassJsonMixin):
    """Fields."""

    values: list

    def serialize(self) -> str:
        """Serialize Fields properties."""
        return serialize_properties(
            *[write_quote_string_no_skip(f"Name{i + 1}", val) for i, val in enumerate(self.values)],
        )

    @classmethod
    def deserialize(cls, data: dict) -> Fields:
        """Deserialize Fields properties."""
        values = []
        i = 1
        while f"Name{i}" in data:
            values.append(data[f"Name{i}"])
            i += 1
        return cls(values=values)

    def encode(self) -> str:
        """Encode fields to a string."""
        out = "{"
        for i in range(len(self.values)):
            out += f'"Name{i}":"{self.values[i]}" '
            if i < len(self.values) - 1:
                out += ","
        out += "}"
        return json.loads(out)


@dataclass_json
@dataclass
class Comment(DataClassJsonMixin):
    """Comment."""

    text: str = string_field()
    """Comment text content."""

    def serialize(self) -> str:
        """Serialize Comment properties."""
        return f"Text:{self.text}"

    @classmethod
    def deserialize(cls, data: dict) -> Comment:
        """Deserialize Comment properties."""
        return cls(text=data.get("Text", ""))

    def encode(self) -> str:
        """Encode comments to a string."""
        out = "{"
        out += f'"Text":"{self.text}"'
        out += "}"
        return json.loads(out)


@dataclass_json
@dataclass
class EfficiencyType(DataClassJsonMixin):
    """Efficiency characteristics for battery charging and discharging.

    Defines efficiency curves as a function of input/output power levels.
    Used for both charging efficiency (as function of input power) and
    discharging efficiency (as function of output power) in battery systems.
    Supports up to 5 points to define the efficiency curve.
    """

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
        """Serialize EfficiencyType properties."""
        return serialize_properties(
            write_double_no_skip("Input1", self.input1),
            write_double_no_skip("Output1", self.output1),
            write_double_no_skip("Input2", self.input2),
            write_double_no_skip("Output2", self.output2),
            write_double_no_skip("Input3", self.input3),
            write_double_no_skip("Output3", self.output3),
            write_double_no_skip("Input4", self.input4),
            write_double_no_skip("Output4", self.output4),
            write_double_no_skip("Input5", self.input5),
            write_double_no_skip("Output5", self.output5),
        )

    @classmethod
    def deserialize(cls, data: dict) -> EfficiencyType:
        """Deserialize EfficiencyType properties."""
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
class QControl(DataClassJsonMixin):
    """Reactive power control for batteries and generators.

    Provides Q(U) voltage-dependent reactive power control or constant cos phi control.
    The Q(U) control adjusts reactive power output based on voltage levels to support
    grid voltage regulation. Constant cos phi control maintains a fixed power factor.
    """

    sort: int = 0
    cosref: float = 0.0
    no_p_no_q: bool = True
    input1: float = 1.0
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
        """Serialize QControl properties."""
        return serialize_properties(
            write_integer("Sort", self.sort, skip=0),
            write_double_no_skip("CosRef", self.cosref),
            write_boolean_no_skip("NoPNoQ", value=self.no_p_no_q),
            write_double_no_skip("Input1", self.input1),
            write_double_no_skip("Output1", self.output1),
            write_double_no_skip("Input2", self.input2),
            write_double_no_skip("Output2", self.output2),
            write_double_no_skip("Input3", self.input3),
            write_double_no_skip("Output3", self.output3),
            write_double_no_skip("Input4", self.input4),
            write_double_no_skip("Output4", self.output4),
            write_double_no_skip("Input5", self.input5),
            write_double_no_skip("Output5", self.output5),
        )

    @classmethod
    def deserialize(cls, data: dict) -> QControl:
        """Deserialize QControl properties."""
        return cls(
            sort=data.get("Sort", 0),
            cosref=data.get("CosRef", 0.0),
            no_p_no_q=data.get("NoPNoQ", True),
            input1=data.get("Input1", 1.0),
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
class PControl(DataClassJsonMixin):
    """Active power control for batteries and generators.

    Supports three control modes:
    - P(U): Voltage-dependent active power control for voltage regulation
    - P(t): Time-based active power control with start/end times for scheduled operation
    - P(I): Current-dependent active power control based on measured field current

    The P(U) and P(I) controls override the generally specified P and profile values.
    The P(t) control overrides these values only when the time is known.
    """

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
        """Serialize PControl properties."""
        return serialize_properties(
            write_integer_no_skip("Sort", self.sort),
            write_double_no_skip("StartTime1", self.start_time1),
            write_double_no_skip("EndTime1", self.end_time1),
            write_double_no_skip("Input1", self.input1),
            write_double_no_skip("Output1", self.output1),
            write_double_no_skip("StartTime2", self.start_time2),
            write_double_no_skip("EndTime2", self.end_time2),
            write_double_no_skip("Input2", self.input2),
            write_double_no_skip("Output2", self.output2),
            write_double_no_skip("StartTime3", self.start_time3),
            write_double_no_skip("EndTime3", self.end_time3),
            write_double_no_skip("Input3", self.input3),
            write_double_no_skip("Output3", self.output3),
            write_double_no_skip("StartTime4", self.start_time4),
            write_double_no_skip("EndTime4", self.end_time4),
            write_double_no_skip("Input4", self.input4),
            write_double_no_skip("Output4", self.output4),
            write_double_no_skip("StartTime5", self.start_time5),
            write_double_no_skip("EndTime5", self.end_time5),
            write_double_no_skip("Input5", self.input5),
            write_double_no_skip("Output5", self.output5),
            write_quote_string_no_skip("MeasureField", self.measure_field),
        )

    @classmethod
    def deserialize(cls, data: dict) -> PControl:
        """Deserialize PControl properties."""
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
