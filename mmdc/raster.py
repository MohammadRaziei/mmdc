"""
mmdc.raster — SVG -> PNG via resvg_py.

`skip_system_fonts=True` + explicit `font_files` means every render uses
exactly the same bundled DejaVu Sans files that mmdc.font_metrics reads for
layout measurement (see engine.py) — the whole point being that mermaid's
layout and the final pixels always agree, regardless of what fonts (if any)
happen to be installed on the host system.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import resvg_py

_FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
_FONT_FILES = [
    str(_FONTS_DIR / "DejaVuSans.ttf"),
    str(_FONTS_DIR / "DejaVuSans-Bold.ttf"),
]
_FAMILY = "DejaVu Sans"


def render_png(svg_text: str, *, scale: float = 1.0, background: Optional[str] = None) -> bytes:
    data = resvg_py.svg_to_bytes(
        svg_string=svg_text,
        background=background,
        skip_system_fonts=True,
        font_files=_FONT_FILES,
        font_family=_FAMILY,
        sans_serif_family=_FAMILY,
        serif_family=_FAMILY,
        cursive_family=_FAMILY,
        fantasy_family=_FAMILY,
        monospace_family=_FAMILY,
        zoom=scale,
    )
    return bytes(data)
