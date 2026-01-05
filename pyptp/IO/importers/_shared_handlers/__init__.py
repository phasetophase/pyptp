# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared handler utilities for GNF and VNF importers."""

from pyptp.IO.importers._shared_handlers.comment_parser import CommentParser
from pyptp.IO.importers._shared_handlers.properties_parser import PropertiesParser

__all__ = ["CommentParser", "PropertiesParser"]
