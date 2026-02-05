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
    Only versions with save modules in the migrator DLL are included.
    G8.9 is the latest format (G8.10 doesn't exist, G8.11 saves as G8.9).
    """

    G8_7 = "G8.7"
    G8_8 = "G8.8"
    G8_9 = "G8.9"


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


class VoltageControlSort(IntEnum):
    """Voltage control type for tap-changing transformers.

    Determines how the automatic voltage control operates.
    """

    COMPOUNDING = 0
    """Compounding control - adjusts setpoint based on current flow."""

    LOAD = 1
    """Load-based control - adjusts voltage based on load conditions."""
