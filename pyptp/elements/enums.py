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
