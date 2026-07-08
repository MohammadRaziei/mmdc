"""
mmdc.diagram — the object returned by mmdc.render().

Mirrors the API of mmdr (https://github.com/mohammadraziei/mmdr): same
.svg()/.png()/.raw()/.numpy()/.save() shape, same _repr_svg_() for
notebooks. Every method here is lazy *and* cached: nothing is computed
until you call it, and calling it again with the same arguments returns
the memoized result instead of recomputing.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from mmdc.ascii import render_ascii
from mmdc.engine import Engine, MermaidRenderError
from mmdc.pdf_writer import png_to_pdf
from mmdc.png_decode import decode_png_rgba, decode_png
from mmdc.raster import render_png

if TYPE_CHECKING:
    import numpy as np

# One persistent, lazily-started engine shared by every render() call in the
# process — loading mermaid.js (~6MB of source) is the expensive part, so it
# only happens once. Synchronous by design: Engine.start()/render_svg()
# already block internally on their own dedicated worker thread, so no
# asyncio is needed here at all.
_engine: Optional[Engine] = None
_engine_lock = threading.Lock()


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:  # re-check inside the lock
                e = Engine()
                e.start()
                _engine = e
    return _engine


_MISSING = object()


class Diagram:
    """A rendered Mermaid diagram (the 'js' backend — see mmdc.render()).

    Every method is lazy and cached: nothing runs until you call it, and
    calling it again with the same arguments returns the memoized result
    rather than recomputing.

    Example::

        import mmdc

        d = mmdc.render("flowchart LR; A-->B-->C")

        d.svg()                          # str -- computed on first call
        d.svg() is d.svg()               # True -- cached, not recomputed
        d.png()                          # bytes (PNG)
        d.png(width=1200, background="#ffffff")   # a different cache entry
        d.raw()                          # (bytes, width, height) — RGBA8888
        d.numpy()                        # np.ndarray, no Pillow needed
        d.ascii()                        # str -- needs mmdc[ascii]
        d.save("out.svg")
        d.save("out.png", width=1200)
        d.save("out.pdf", pdf_format="A4", pdf_margin="1cm")
        d.save("out.png.bak", format="png")   # force format regardless of extension
    """

    def __init__(
        self,
        source: str,
        *,
        theme: Optional[str] = None,
        config: Optional[dict] = None,
        css: Optional[str] = None,
        **_ignored,
    ) -> None:
        self._source = source
        self._theme = theme
        self._config = config
        self._css = css
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # memoization helper -- keyed by (method name, sorted kwargs)
    # ------------------------------------------------------------------

    def _cached(self, name: str, kwargs: dict, compute):
        key = (name, tuple(sorted(kwargs.items())))
        result = self._cache.get(key, _MISSING)
        if result is _MISSING:
            result = compute()
            self._cache[key] = result
        return result

    # ------------------------------------------------------------------
    # SVG — lazy, cached
    # ------------------------------------------------------------------

    def svg(self) -> str:
        """Return the diagram as an SVG string (rendered once, then cached)."""
        def _compute():
            try:
                return _get_engine().render_svg(
                    self._source, self._theme or "default", self._config, self._css
                )
            except MermaidRenderError as e:
                raise RuntimeError(f"Mermaid rendering failed: {e}") from e
        return self._cached("svg", {}, _compute)

    # ------------------------------------------------------------------
    # Rasterization — lazy, cached, via resvg
    # ------------------------------------------------------------------

    def png(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        background: Optional[str] = None,
    ) -> bytes:
        """Return the diagram as PNG bytes.

        Args:
            width:      Canvas width hint in pixels.
            height:     Canvas height hint in pixels.
            scale:      Size multiplier, used only if width/height are both omitted
                        (e.g. scale=2.0 for a "2x" render at the diagram's natural size).
            background: CSS color, e.g. ``"#ffffff"``. Transparent by default.

        Note:
            Aspect ratio is always preserved (like most SVG rasterizers).
            If both width and height are given, width wins and height is
            derived from it -- this never stretches the diagram.
        """
        def _compute():
            kwargs = dict(background=background, width=width, height=height)
            if width is None and height is None and scale is not None:
                kwargs["scale"] = scale
            return render_png(self.svg(), **kwargs)
        return self._cached(
            "png", dict(width=width, height=height, scale=scale, background=background), _compute
        )

    def raw(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        background: Optional[str] = None,
    ) -> tuple[bytes, int, int]:
        """Return raw RGBA8888 pixels as ``(bytes, width, height)`` — no
        imaging library involved, just resvg's output decoded directly."""
        def _compute():
            png_bytes = self.png(width=width, height=height, scale=scale, background=background)
            return decode_png_rgba(png_bytes)
        return self._cached(
            "raw", dict(width=width, height=height, scale=scale, background=background), _compute
        )

    def numpy(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        background: Optional[str] = None,
    ) -> "np.ndarray":
        """Return an ``(H, W, 4)`` uint8 RGBA array. Requires ``numpy``."""
        try:
            import numpy as np
        except ImportError as exc:
            raise ImportError(
                "numpy is required for .numpy(). Install it with:\n"
                "    pip install numpy"
            ) from exc

        def _compute():
            raw, w, h = self.raw(width=width, height=height, scale=scale, background=background)
            return np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
        return self._cached(
            "numpy", dict(width=width, height=height, scale=scale, background=background), _compute
        )

    def pdf(
        self,
        *,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: float = 1.0,
        background: Optional[str] = None,
        pdf_format: Optional[str] = None,
        pdf_landscape: bool = False,
        pdf_margin: str = "0",
    ) -> bytes:
        """Return the diagram as PDF bytes (fully supported — no imaging
        library needed here either: a hand-written, dependency-free PDF
        writer embeds the resvg-rendered pixels directly).

        Args:
            width, height: Canvas size in pixels (only when pdf_format is None --
                            with a fixed pdf_format the paper size wins instead).
            scale:         Resolution multiplier, used if width/height are omitted
                           (only when pdf_format is None).
            background:    CSS color for the page background.
            pdf_format:    Paper format e.g. ``"A4"``, ``"Letter"``. None = fit to diagram.
            pdf_landscape: Landscape orientation.
            pdf_margin:    CSS-style margin e.g. ``"1cm"`` (only with pdf_format).
        """
        def _compute():
            render_kwargs = dict(background=background, width=width, height=height)
            if width is None and height is None:
                render_kwargs["scale"] = scale
            png_bytes = render_png(self.svg(), **render_kwargs)
            decoded = decode_png(png_bytes)
            return png_to_pdf(
                decoded, pdf_format=pdf_format, landscape=pdf_landscape,
                margin=pdf_margin, scale=1.0, background_color=background,
            )
        return self._cached(
            "pdf",
            dict(width=width, height=height, scale=scale, background=background,
                 pdf_format=pdf_format, pdf_landscape=pdf_landscape, pdf_margin=pdf_margin),
            _compute,
        )

    def ascii(self, **opts) -> str:
        """Return the diagram as ASCII/Unicode box-drawing art.

        Requires the optional ``termaid`` package::

            pip install mmdc[ascii]

        Rendered straight from the Mermaid source (termaid has its own
        parser -- it doesn't go through the SVG at all), so it's available
        even if .svg() was never called.
        """
        return self._cached("ascii", opts, lambda: render_ascii(self._source, **opts))

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    _EXTENSION_FORMATS = {".svg": "svg", ".png": "png", ".pdf": "pdf",
                          ".txt": "ascii", ".ascii": "ascii"}

    def save(
        self,
        output: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scale: Optional[float] = None,
        background: Optional[str] = None,
        format: Optional[str] = None,
        **format_opts,
    ) -> None:
        """Save the diagram to *output*.

        Args:
            format: Force the output format ("svg", "png", "pdf", or "ascii")
                    regardless of the file extension. If omitted (the
                    default), the format is inferred from *output*'s
                    extension: ``.svg``, ``.png``, ``.pdf``, or ``.txt``/``.ascii``.
            **format_opts: Forwarded to the matching method -- pdf_format/
                    pdf_landscape/pdf_margin for "pdf", any termaid option for "ascii".

        Raises:
            ValueError: if the format can't be determined, or is unrecognised.
        """
        path = Path(output)
        fmt = format or self._EXTENSION_FORMATS.get(path.suffix.lower())
        if fmt is None:
            raise ValueError(
                f"Cannot infer output format from {output!r}. "
                "Pass format=\"svg\"/\"png\"/\"pdf\"/\"ascii\" explicitly, "
                "or use one of these extensions: "
                f"{sorted(set(self._EXTENSION_FORMATS))}"
            )

        if fmt == "svg":
            path.write_text(self.svg(), encoding="utf-8")
        elif fmt == "png":
            path.write_bytes(self.png(width=width, height=height, scale=scale, background=background))
        elif fmt == "pdf":
            path.write_bytes(self.pdf(
                width=width, height=height, scale=scale or 1.0,
                background=background, **format_opts,
            ))
        elif fmt == "ascii":
            path.write_text(self.ascii(**format_opts), encoding="utf-8")
        else:
            raise ValueError(
                f"Unknown format {fmt!r}. Supported: svg, png, pdf, ascii"
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        first_line = (self._source.strip().splitlines() or [""])[0]
        return f"<Diagram backend='js' {first_line!r}>"

    def _repr_svg_(self) -> str:
        """Jupyter/IPython rich display — renders inline SVG automatically."""
        return self.svg()


def render(source: str, backend: Optional[str] = None, **opts) -> "Diagram":
    """
    Render a Mermaid diagram.

    Args:
        source:  Mermaid source text.
        backend: ``'js'`` (default — this package's own QuickJS + resvg
                 engine, always available, zero extra dependencies) or, if
                 the optional ``mmdr`` package is installed,
                 ``'merman'`` / ``'mermaid-rs-renderer'``.
        **opts:  Forwarded to the chosen backend.
                 'js': theme, config, css
                 mmdr backends: theme, node_spacing, rank_spacing, aspect_ratio

    Returns:
        A Diagram. Every method (svg/png/raw/numpy/pdf/ascii) is lazy and
        cached. When delegating to an ``mmdr`` backend, this returns
        *mmdr's own* Diagram object directly — its API is identical by
        design, so no wrapping is needed.
    """
    if backend in (None, "js"):
        return Diagram(source, **opts)

    from .backends import backends

    try:
        import mmdr
    except ImportError as exc:
        raise ImportError(
            f"backend={backend!r} requires the optional 'mmdr' package. "
            "Install it with:\n    pip install mmdc[rust]"
        ) from exc

    if backend not in mmdr.backends():
        raise ValueError(f"Unknown backend {backend!r}. Available: {backends()!r}")
    return mmdr.render(source, backend=backend, **opts)
