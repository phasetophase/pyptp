# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Errors raised while reading a type workbook."""

from __future__ import annotations


class UnknownTypeError(LookupError):
    """Raised when the type workbook has no type under the requested name."""


class MissingSheetError(LookupError):
    """Raised when the type workbook has no sheet for the requested kind of type."""
