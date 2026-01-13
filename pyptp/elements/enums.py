"""Shared enums for electrical network elements."""

from __future__ import annotations

from enum import IntEnum


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
