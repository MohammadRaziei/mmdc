"""
mmdc — Mermaid diagram converter backed by a persistent QuickJS session.

One MermaidConverter instance = one QuickJS context with mermaid.js loaded,
reused across all conversions, pinned to a single dedicated worker thread.
Supports SVG, PNG, and PDF output. Works fully offline and without any
browser, Node.js, or npm — the Mermaid JS library is bundled inside the
package and executed in a small embedded JS engine (QuickJS-ng); text
metrics (the one thing a fake DOM can't fabricate) are computed for real via
Cairo, the same library used for the final SVG->PNG/PDF conversion.

Usage
-----
    import asyncio
    from mmdc import MermaidConverter

    async def main():
        async with MermaidConverter() as m:
            svg = await m.to_svg("graph TD\\nA-->B")
            png = await m.to_png("graph TD\\nA-->B", scale=2.0)
            await m.to_pdf("graph LR\\nA-->B", output="diagram.pdf")

    asyncio.run(main())
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Optional, Union

from mmdc.engine import Engine, MermaidRenderError
from mmdc.png_decode import decode_png
from mmdc.raster import render_png
from mmdc.pdf_writer import png_to_pdf

# Assets bundled inside the package
_ASSETS_DIR = Path(__file__).parent / "assets"


# ── helpers ───────────────────────────────────────────────────────────────────

def _read_input(source: Union[str, Path]) -> str:
    """Accept a Mermaid string, a .mermaid/.md file path string, or a Path."""
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    p = Path(source)
    if p.suffix.lower() in (".mermaid", ".md", ".txt") and p.is_file():
        return p.read_text(encoding="utf-8")
    return source  # raw mermaid string


def _parse_svg_dimensions(svg_text):
    """
    Extract width/height from SVG string.
    Falls back to viewBox if width/height are missing or non-numeric (e.g. "100%").
    Returns (w, h) as integers or (None, None).
    """
    if isinstance(svg_text, bytes):
        svg_text = svg_text.decode("utf-8", errors="ignore")

    m = re.search(r'<svg[^>]*>', svg_text, re.DOTALL)
    if not m:
        return None, None

    tag = m.group(0)

    def _attr_int(name: str):
        am = re.search(rf'{name}\s*=\s*["\']([^"\']+)["\']', tag)
        if not am:
            return None
        val = am.group(1).strip().rstrip("px").strip()
        try:
            v = int(float(val))
            return v if v > 0 else None
        except ValueError:
            return None  # "100%" etc.

    w = _attr_int("width")
    h = _attr_int("height")

    if w is None or h is None:
        vb = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', tag)
        if vb:
            parts = vb.group(1).strip().split()
            if len(parts) == 4:
                try:
                    w = w or int(float(parts[2]))
                    h = h or int(float(parts[3]))
                except ValueError:
                    pass

    return w, h


# ── MermaidConverter ──────────────────────────────────────────────────────────

class MermaidConverter:
    """
    Persistent Mermaid diagram converter backed by a single QuickJS context.

    Use as an async context manager (recommended):

        async with MermaidConverter() as m:
            svg = await m.to_svg("graph TD\\nA-->B")
            png = await m.to_png("sequenceDiagram\\nA->>B: Hello", scale=2.0)
            await m.to_pdf("graph LR\\nA-->B", output="out.pdf")

    Or manage lifecycle manually:

        m = MermaidConverter()
        await m.start()
        svg = await m.to_svg("graph TD\\nA-->B")
        await m.close()
    """

    def __init__(self, theme: str = "default", background: str = "white") -> None:
        """
        Parameters
        ----------
        theme:      Default Mermaid theme: "default", "forest", "dark", "neutral".
        background: Default page background color.
        """
        self._default_theme = theme
        self._default_background = background
        self._engine: Optional[Engine] = None

    # ── lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> "MermaidConverter":
        """Start the embedded JS engine and load mermaid.js."""
        engine = Engine()
        await asyncio.to_thread(engine.start)
        self._engine = engine
        return self

    async def close(self) -> None:
        """Shut down the embedded JS engine."""
        if self._engine is not None:
            await asyncio.to_thread(self._engine.close)
            self._engine = None

    async def __aenter__(self) -> "MermaidConverter":
        return await self.start()

    async def __aexit__(self, *_) -> None:
        await self.close()

    # ── internal render ───────────────────────────────────────────────────────

    async def _render_svg(
        self,
        code: str,
        theme: str,
        config: Optional[dict],
        css: Optional[str],
    ) -> str:
        if self._engine is None:
            raise RuntimeError(
                "MermaidConverter is not started. Use 'async with' or call start() first."
            )
        try:
            return await asyncio.to_thread(self._engine.render_svg, code, theme, config, css)
        except MermaidRenderError as e:
            raise RuntimeError(f"Mermaid rendering failed: {e}") from e

    async def _render(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]],
        fmt: str,
        theme: Optional[str],
        background: Optional[str],
        scale: float,
        config: Optional[dict],
        css: Optional[str],
        pdf_format: Optional[str],
        pdf_landscape: bool,
        pdf_margin: str,
    ) -> bytes:
        code       = _read_input(source)
        theme      = theme      or self._default_theme
        background = background or self._default_background

        if self._engine is None:
            raise RuntimeError(
                "MermaidConverter is not started. Use 'async with' or call start() first."
            )

        svg = await self._render_svg(code, theme, config, css)

        if fmt == "svg":
            data = svg.encode("utf-8")
            if output:
                Path(output).write_bytes(data)
            return data

        svg_bytes = svg.encode("utf-8")

        if fmt == "png":
            data = await asyncio.to_thread(render_png, svg, scale=scale, background=background)
        elif fmt == "pdf":
            # Render at the target resolution directly (rather than rendering at
            # 1x and stretching in the PDF page), so `scale` actually improves
            # sharpness instead of just blowing up the same pixels.
            png_bytes = await asyncio.to_thread(render_png, svg, scale=scale, background=background)
            decoded = await asyncio.to_thread(decode_png, png_bytes)
            data = await asyncio.to_thread(
                png_to_pdf,
                decoded, pdf_format=pdf_format, landscape=pdf_landscape,
                margin=pdf_margin, scale=1.0, background_color=background,
            )
        else:
            raise ValueError(f"Unsupported format: {fmt!r}")

        if output:
            Path(output).write_bytes(data)
        return data

    # ── public API ────────────────────────────────────────────────────────────

    async def to_svg(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        *,
        theme: Optional[str] = None,
        background: Optional[str] = None,
        config: Optional[dict] = None,
        css: Optional[str] = None,
    ) -> bytes:
        """
        Render Mermaid diagram to SVG.

        Parameters
        ----------
        source:     Mermaid string, file path string, or Path object.
        output:     Optional file path to write the result.
        theme:      Mermaid theme override ("default", "forest", "dark", "neutral").
        background: CSS background color.
        config:     Mermaid config dict (merged with defaults).
        css:        Inline CSS injected into the diagram.

        Returns SVG bytes.
        """
        return await self._render(
            source, output, "svg",
            theme, background, 1.0,
            config, css, None, False, "0",
        )

    async def to_png(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        *,
        scale: float = 1.0,
        theme: Optional[str] = None,
        background: Optional[str] = None,
        config: Optional[dict] = None,
        css: Optional[str] = None,
    ) -> bytes:
        """
        Render Mermaid diagram to PNG.

        Parameters
        ----------
        source:     Mermaid string, file path string, or Path object.
        output:     Optional file path to write the result.
        scale:      Size multiplier (e.g. 2.0 for 2x resolution).
        theme:      Mermaid theme override.
        background: CSS background color.
        config:     Mermaid config dict.
        css:        Inline CSS.

        Returns PNG bytes.
        """
        return await self._render(
            source, output, "png",
            theme, background, scale,
            config, css, None, False, "0",
        )

    async def to_pdf(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        *,
        scale: float = 1.0,
        theme: Optional[str] = None,
        background: Optional[str] = None,
        config: Optional[dict] = None,
        css: Optional[str] = None,
        pdf_format: Optional[str] = None,
        pdf_landscape: bool = False,
        pdf_margin: str = "0",
    ) -> bytes:
        """
        Render Mermaid diagram to PDF.

        Parameters
        ----------
        source:         Mermaid string, file path string, or Path object.
        output:         Optional file path to write the result.
        scale:          Size multiplier (applies only when pdf_format is None).
        theme:          Mermaid theme override.
        background:     CSS background color.
        config:         Mermaid config dict.
        css:            Inline CSS.
        pdf_format:     Paper format e.g. "A4", "Letter". None (default) = fit to diagram.
        pdf_landscape:  Landscape orientation.
        pdf_margin:     CSS-style margin e.g. "1cm" (default: "0").

        Returns PDF bytes.
        """
        return await self._render(
            source, output, "pdf",
            theme, background, scale,
            config, css, pdf_format, pdf_landscape, pdf_margin,
        )

    async def convert(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        *,
        scale: float = 1.0,
        theme: Optional[str] = None,
        background: Optional[str] = None,
        config: Optional[dict] = None,
        css: Optional[str] = None,
        **kwargs,
    ) -> bytes:
        """
        Convert Mermaid diagram to SVG/PNG/PDF based on output file extension.
        Falls back to SVG if no output is given.

        Format-specific options can be passed via **kwargs and are forwarded
        to the appropriate method:
            PNG: scale (already a common param)
            PDF: pdf_format, pdf_landscape, pdf_margin
        """
        common = dict(theme=theme, background=background, config=config, css=css)

        if output is None:
            return await self.to_svg(source, **common)

        ext = Path(output).suffix.lower()
        if ext == ".svg":
            return await self.to_svg(source, output, **common)
        elif ext == ".png":
            return await self.to_png(source, output, scale=scale, **common)
        elif ext == ".pdf":
            return await self.to_pdf(source, output, scale=scale, **common, **kwargs)
        else:
            raise ValueError(f"Unsupported output format: {ext!r}. Use .svg, .png, or .pdf")


# ── module-level singleton ────────────────────────────────────────────────────

import atexit as _atexit

_default: Optional[MermaidConverter] = None


def _get_default() -> MermaidConverter:
    """Return the module-level singleton, creating it if needed."""
    global _default
    if _default is None:
        _default = MermaidConverter()
    return _default


def _shutdown_default() -> None:
    """Called at interpreter exit — closes the singleton if it was started."""
    global _default
    if _default is not None and _default._engine is not None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_default.close())
            else:
                loop.run_until_complete(_default.close())
        except Exception:
            pass
        _default = None


_atexit.register(_shutdown_default)


async def _ensure_started() -> MermaidConverter:
    """Return the singleton, starting it on first use."""
    m = _get_default()
    if m._engine is None:
        await m.start()
    return m


async def to_svg(source: Union[str, Path], output=None, **kwargs) -> bytes:
    """Module-level to_svg — uses a shared persistent session."""
    return await (await _ensure_started()).to_svg(source, output, **kwargs)


async def to_png(source: Union[str, Path], output=None, **kwargs) -> bytes:
    """Module-level to_png — uses a shared persistent session."""
    return await (await _ensure_started()).to_png(source, output, **kwargs)


async def to_pdf(source: Union[str, Path], output=None, **kwargs) -> bytes:
    """Module-level to_pdf — uses a shared persistent session."""
    return await (await _ensure_started()).to_pdf(source, output, **kwargs)


async def convert(source: Union[str, Path], output=None, **kwargs) -> bytes:
    """Module-level convert — uses a shared persistent session."""
    return await (await _ensure_started()).convert(source, output, **kwargs)
