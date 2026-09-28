"""Workbook header renames for the MV type sheets."""

from __future__ import annotations

DEFAULT_CABLE_RENAME = {
    # Workbook headers that differ from the VNF property name by more than
    # case.
    "Tan_delta": "TanDelta",
    "VoP": "PulseVelocity",
}
