"""Workbook header renames for the LV type sheets."""

from __future__ import annotations

# These columns are spelled with either a _T or a _O suffix. The GNF property
# name uses _o, so only _T needs a rename.
DEFAULT_CABLE_RENAME = {
    "R_CC_T": "R_cc_o",
    "X_CC_T": "X_cc_o",
    "R_CH_T": "R_ch_o",
    "X_CH_T": "X_ch_o",
    "R_HH_T": "R_hh_o",
    "X_HH_T": "X_hh_o",
}
