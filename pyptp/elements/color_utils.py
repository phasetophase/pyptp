"""color_utils.py.

Defines DelphiColor constants and dataclass Field factories for common colors.
"""

from typing import NewType

"""DelphiColor is a type alias for a string representing a Delphi color.

More context about Colors in Delphi Pascal can be found here https://docwiki.embarcadero.com/Libraries/en/Vcl.Graphics.TColor
"""
DelphiColor = NewType("DelphiColor", str)

# Basic colors
CL_BLACK = DelphiColor("$000000")
"""Black."""

CL_MAROON = DelphiColor("$000080")
"""Maroon."""

CL_GREEN = DelphiColor("$008000")
"""Green."""

CL_OLIVE = DelphiColor("$008080")
"""Olive Green."""

CL_NAVY = DelphiColor("$800000")
"""Navy Blue."""

CL_PURPLE = DelphiColor("$800080")
"""Purple."""

CL_TEAL = DelphiColor("$808000")
"""Teal."""

CL_GRAY = DelphiColor("$808080")
"""Gray."""

CL_SILVER = DelphiColor("$C0C0C0")
"""Silver."""

CL_RED = DelphiColor("$0000FF")
"""Red."""

CL_LIME = DelphiColor("$00FF00")
"""Lime Green."""

CL_YELLOW = DelphiColor("$00FFFF")
"""Yellow."""

CL_BLUE = DelphiColor("$FF0000")
"""Blue."""

CL_FUCHSIA = DelphiColor("$FF00FF")
"""Fuchsia."""

CL_AQUA = DelphiColor("$FFFF00")
"""Aqua."""

CL_WHITE = DelphiColor("$FFFFFF")
"""White."""

CL_MONEY_GREEN = DelphiColor("$C0DCC0")
"""Mint Green."""

CL_SKY_BLUE = DelphiColor("$F0CAA6")
"""Sky Blue."""

CL_CREAM = DelphiColor("$F0FBFF")
"""Cream."""

CL_MED_GRAY = DelphiColor("$A4A0A0")
"""Medium Gray."""

CL_NONE = DelphiColor("$1FFFFFFF")
"""No color (transparent/none)."""

# Modern extended colors for electrical diagrams
CL_DARK_BLUE = DelphiColor("$8B0000")
"""Dark Blue."""

CL_ORANGE = DelphiColor("$00A5FF")
"""Orange."""

CL_LIGHT_BLUE = DelphiColor("$FFE4B5")
"""Light Blue."""

CL_DARK_GREEN = DelphiColor("$006400")
"""Dark Green."""

CL_LIGHT_GREEN = DelphiColor("$90EE90")
"""Light Green."""

CL_DARK_GRAY = DelphiColor("$404040")
"""Dark Gray."""

CL_LIGHT_GRAY = DelphiColor("$E0E0E0")
"""Light Gray."""

CL_INDIGO = DelphiColor("$82004B")
"""Indigo."""

CL_VIOLET = DelphiColor("$EE82EE")
"""Violet."""

CL_CORAL = DelphiColor("$507FFF")
"""Coral."""

CL_TURQUOISE = DelphiColor("$D0E040")
"""Turquoise."""

CL_GOLD = DelphiColor("$00D7FF")
"""Gold."""

CL_PINK = DelphiColor("$CBC0FF")
"""Pink."""

CL_BROWN = DelphiColor("$2A2AA5")
"""Brown."""

CL_BEIGE = DelphiColor("$DCF5F5")
"""Beige."""

# Dark mode specific colors
CL_CHARCOAL = DelphiColor("$202020")
"""Dark charcoal for dark backgrounds."""

CL_BRIGHT_GOLD = DelphiColor("$FFD700")
"""Bright gold for high visibility."""

CL_BRIGHT_CYAN = DelphiColor("$00FFFF")
"""Bright cyan."""

CL_BRIGHT_LIME = DelphiColor("$00FF00")
"""Bright lime green."""

CL_HOT_PINK = DelphiColor("$FF1493")
"""Hot pink."""

CL_TOMATO = DelphiColor("$FF6347")
"""Tomato red."""

CL_ORCHID = DelphiColor("$DA70D6")
"""Orchid purple."""

CL_DARK_TURQUOISE = DelphiColor("$00CED1")
"""Dark turquoise."""

# High contrast colors
CL_STRONG_BLUE = DelphiColor("$0000CC")
"""Strong blue for high contrast."""

CL_STRONG_RED = DelphiColor("$CC0000")
"""Strong red for high contrast."""

CL_STRONG_ORANGE = DelphiColor("$FF8000")
"""Strong orange for high contrast."""

CL_STRONG_PURPLE = DelphiColor("$800080")
"""Strong purple for high contrast."""

CL_DARK_RED = DelphiColor("$8B0000")
"""Dark red."""


class ColorPalette:
    """Color palette for electrical network diagrams."""

    def __init__(
        self,
        background: DelphiColor,
        nodes: DelphiColor,
        cables: DelphiColor,
        transformers: DelphiColor,
        loads: DelphiColor,
        transformer_loads: DelphiColor,
        sources: DelphiColor,
        text: DelphiColor,
        links: DelphiColor,
        generators: DelphiColor,
    ) -> None:
        """Initialize color palette."""
        self.background = background
        self.nodes = nodes
        self.cables = cables
        self.transformers = transformers
        self.loads = loads
        self.transformer_loads = transformer_loads
        self.sources = sources
        self.text = text
        self.links = links
        self.generators = generators


# Light mode palette (modern, clean)
LIGHT_PALETTE = ColorPalette(
    background=CL_WHITE,  # Clean white background
    nodes=CL_DARK_BLUE,  # Professional dark blue nodes
    cables=CL_DARK_GRAY,  # Dark gray cables
    transformers=CL_INDIGO,  # Indigo transformers
    loads=CL_DARK_GREEN,  # Dark green loads
    transformer_loads=CL_ORANGE,  # Orange transformer loads
    sources=CL_RED,  # Red sources (grid connection)
    text=CL_BLACK,  # Black text for readability
    links=CL_PURPLE,  # Purple links (mesh connections)
    generators=CL_TURQUOISE,  # Turquoise generators/renewables
)

# Dark mode palette (modern, professional)
DARK_PALETTE = ColorPalette(
    background=CL_CHARCOAL,  # Dark charcoal background
    nodes=CL_BRIGHT_GOLD,  # Bright gold nodes for high visibility
    cables=CL_LIGHT_GRAY,  # Light gray cables for clear routing
    transformers=CL_BRIGHT_CYAN,  # Bright cyan transformers
    loads=CL_BRIGHT_LIME,  # Bright lime green loads
    transformer_loads=CL_HOT_PINK,  # Bright deep pink transformer loads
    sources=CL_TOMATO,  # Bright tomato red sources
    text=CL_WHITE,  # White text for dark background
    links=CL_ORCHID,  # Bright orchid links
    generators=CL_DARK_TURQUOISE,  # Bright dark turquoise generators
)

# Classic palette (traditional electrical colors)
CLASSIC_PALETTE = ColorPalette(
    background=CL_CREAM,  # Traditional cream background
    nodes=CL_BLACK,  # Black nodes
    cables=CL_BLACK,  # Black cables
    transformers=CL_NAVY,  # Navy transformers
    loads=CL_GREEN,  # Green loads
    transformer_loads=CL_OLIVE,  # Olive transformer loads
    sources=CL_RED,  # Red sources
    text=CL_BLACK,  # Black text
    links=CL_PURPLE,  # Purple links
    generators=CL_TEAL,  # Teal generators
)

# High contrast palette (accessibility)
HIGH_CONTRAST_PALETTE = ColorPalette(
    background=CL_WHITE,  # White background
    nodes=CL_BLACK,  # Black nodes for maximum contrast
    cables=CL_DARK_GRAY,  # Dark gray cables for visibility
    transformers=CL_STRONG_BLUE,  # Strong blue transformers
    loads=CL_STRONG_RED,  # Strong red loads
    transformer_loads=CL_STRONG_ORANGE,  # Strong orange transformer loads
    sources=CL_STRONG_PURPLE,  # Strong purple sources
    text=CL_BLACK,  # Black text for maximum readability
    links=CL_DARK_RED,  # Dark red links
    generators=CL_DARK_GREEN,  # Dark green generators
)

# Available palettes
PALETTES = {
    "light": LIGHT_PALETTE,
    "dark": DARK_PALETTE,
    "classic": CLASSIC_PALETTE,
    "high_contrast": HIGH_CONTRAST_PALETTE,
}


def get_palette(palette_name: str = "light") -> ColorPalette:
    """Get a color palette by name.

    Args:
        palette_name: Name of the palette ('light', 'dark', 'classic', 'high_contrast')

    Returns:
        ColorPalette object

    """
    return PALETTES.get(palette_name.lower(), LIGHT_PALETTE)
