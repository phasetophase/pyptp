"""Shared enums for electrical network elements."""

from __future__ import annotations

from enum import IntEnum, StrEnum


class SpecialTransformerSort(IntEnum):
    """Special transformer type classification.

    Integer values are non-sequential to maintain compatibility with
    Vision/Gaia file formats. The groupings reflect functional categories:
    - 0-4: Standard and autotransformer variants
    - 11-14: Regulating transformers (booster, phase-shifting)
    - 21, 31: Specialized types
    """

    NONE = 0
    """No special transformer type."""

    AUTO_YD11 = 1
    """Autotransformer with Yd11 vector group."""

    AUTO_YA0 = 2
    """Autotransformer with Ya0 vector group."""

    AUTO_YNA0 = 3
    """Autotransformer with YNa0 vector group (neutral accessible)."""

    AUTO_YNA0_ASYM = 4
    """Autotransformer with YNa0 vector group, asymmetric configuration."""

    BOOSTER = 11
    """Booster transformer for voltage regulation."""

    QUADRATURE_BOOSTER = 12
    """Quadrature booster (phase-shifting transformer)."""

    SCOTT_RS = 13
    """Scott transformer, RS configuration."""

    SCOTT_RT = 14
    """Scott transformer, RT configuration."""

    AXA = 21
    """Axa type transformer."""

    RELO = 31
    """Relo type transformer."""


class NodePresentationSymbol(IntEnum):
    """Node presentation symbol types for graphical network display.

    Defines the visual symbol shapes used to represent nodes in electrical network
    diagrams within Gaia (LV) and Vision (MV) software. Integer values are
    non-sequential to maintain compatibility with the native file format encoding.

    Symbol categories:
    - 1-2: Line symbols
    - 11-13: Circle variants
    - 21-23: Square variants
    - 31-32: Triangle variants
    - 41-42: Diamond variants
    - 51-53: Rectangle variants

    The "open", "closed", and "half-open" terminology refers to whether the symbol
    is filled (closed), outlined only (open), or partially filled (half-open).
    """

    VERTICAL_LINE = 1
    HORIZONTAL_LINE = 2
    CLOSED_CIRCLE = 11
    OPEN_CIRCLE = 12
    HALF_OPEN_CIRCLE = 13
    CLOSED_SQUARE = 21
    OPEN_SQUARE = 22
    HALF_OPEN_SQUARE = 23
    CLOSED_TRIANGLE = 31
    OPEN_TRIANGLE = 32
    CLOSED_DIAMOND = 41
    OPEN_DIAMOND = 42
    CLOSED_RECTANGLE = 51
    OPEN_RECTANGLE = 52
    HALF_OPEN_RECTANGLE = 53


class GnfVersion(StrEnum):
    """GNF (Gaia/LV) file format versions supported for saving.

    Values correspond to version strings written to the first line of GNF files.
    G8.12 is the latest format and the one pyptp models natively; saving to any
    older version writes a native G8.12 file and lets the migrator down-convert.
    """

    G8_7 = "G8.7"
    G8_8 = "G8.8"
    G8_9 = "G8.9"
    G8_11 = "G8.11"
    G8_12 = "G8.12"


class VnfVersion(StrEnum):
    """VNF (Vision/MV) file format versions supported for saving.

    Values correspond to version strings written to the first line of VNF files.
    Only versions with save modules in the migrator DLL are included.
    """

    V9_7 = "V9.7"
    V9_8 = "V9.8"
    V9_9 = "V9.9"
    V9_10 = "V9.10"
    V9_11 = "V9.11"
    V9_12 = "V9.12"


class InsulationCondition(StrEnum):
    """Insulation condition classification for transformer paper.

    Describes the paper insulation condition based on whether it was
    produced air-free, and its moisture content percentage.
    """

    AIR_FREE_MOIST_0_5 = "Free0.5"
    AIR_FREE_MOIST_1_5 = "Free1.5"
    AIR_FREE_MOIST_3_5 = "Free3.5"
    WITH_AIR_MOIST_0_5 = "Air0.5"


class EnclosureType(StrEnum):
    """Transformer enclosure type classification.

    Determines the cooling conditions for thermal modeling.
    """

    OUTSIDE = "Outside"
    VAULT_NATURAL = "VaultNat"
    BASEMENT_POOR_VENT = "BasementPoor"
    VAULT_BASEMENT_FORCED = "ForcedVent"
    KIOSK = "Kiosk"


class ConnectionSort(StrEnum):
    """Connection type classification for LV customer connections."""

    COMBI = "Combi"
    SMALL_CUSTOMER = "SmallCustomer"
    LARGE_CUSTOMER = "LargeCustomer"
    LIGHT = "Light"
    CHARGE = "Charge"
    PV = "PV"
    WIND = "Wind"


class HeatpumpSort(StrEnum):
    """Heatpump type classification."""

    ONE_KW = "1 kW"
    GROUND = "Ground"
    AIR = "Air"


class HouseType(StrEnum):
    """House type classification for heatpump modeling."""

    UNKNOWN = "Unknown"
    TERRACED = "Terraced"
    CORNER = "Corner"
    SEMIDETACHED = "Semidetached"
    DETACHED = "Detached"
    APARTMENT = "Apartment"


class VoltageControlStatus(IntEnum):
    """Operating status of the voltage control."""

    OFF = 0
    """Voltage control is off."""

    OWN = 1
    """Voltage control operates on its own measurement."""

    MASTER = 2
    """Voltage control acts as master."""

    MASTER_OWN = 3
    """Voltage control acts as master with own standby"""


class VoltageControlSort(IntEnum):
    """Voltage control type for tap-changing transformers."""

    COMPOUNDING = 0
    """Compounding control - adjusts setpoint based on current flow."""

    LOAD1 = 1
    """Load-based control - adjusts voltage based on load conditions 1."""

    LOAD2 = 2
    """Load-based control - adjusts voltage based on load conditions 2."""

    LOAD3 = 3
    """Load-based control - adjusts voltage based on load conditions 3."""

    LOAD4 = 4
    """Load-based control - adjusts voltage based on load conditions 4."""


class SpecialVoltageControlSort(IntEnum):
    """Voltage control type for special transformers."""

    COMPOUNDING = 0
    """Compounding control - adjusts setpoint based on current flow."""

    LOAD = 1
    """Load-based control - adjusts voltage based on load conditions."""


class SpecialVoltageControlStatus(IntEnum):
    """Operating status of the special transformer voltage control."""

    OFF = 0
    """Voltage control is off."""

    ON = 1
    """Voltage control is on."""
