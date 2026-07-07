"""
mmdc.engine — headless Mermaid → SVG rendering without a browser.

Architecture
------------
mermaid.js (v11, ES2020+) is executed inside QuickJS-ng (a small, actively
maintained JS engine — NOT the browser-less-but-limited original QuickJS,
which lacks class static blocks used by mermaid's dependencies).

Since QuickJS has no DOM, a minimal fake DOM/SVG implementation is loaded
first (assets/dom_shim.js). The one piece a fake DOM cannot fabricate on its
own — real text metrics (`getBBox` / `getComputedTextLength`) — is bridged
back into Python, where mmdc.font_metrics reads real glyph advance widths
from a bundled font file (DejaVu Sans). The same font file is handed to
resvg for final rendering (see mmdc.py), so the layout mermaid computes
always matches what actually gets painted — by construction, not by luck.

A dedicated single-thread executor owns the QuickJS context, since QuickJS
contexts are not thread-safe and must always be driven from one thread.
"""

from __future__ import annotations

import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import quickjs

from mmdc.font_metrics import get_font

_ASSETS_DIR = Path(__file__).parent / "assets"
_DOM_SHIM_JS = _ASSETS_DIR / "dom_shim.js"
_MERMAID_JS = _ASSETS_DIR / "mermaid.js"

_RENDER_TIMEOUT_JOBS = 200_000  # safety cap on Promise-job pump iterations


class MermaidRenderError(RuntimeError):
    """Raised when mermaid.js itself reports a parse/render error."""


class _TextMeasurer:
    """Real font metrics via mmdc.font_metrics (bundled DejaVu Sans) —
    the same font file resvg is told to use for final rendering, so layout
    and paint always agree (see Engine._init_context / mmdc.py)."""

    def width(self, text, size, family, weight, style) -> float:
        return get_font(weight).measure(text or "", float(size or 16))["width"]

    def full(self, text, size, family, weight, style) -> dict:
        return get_font(weight).measure(text or "", float(size or 16))


def _path_bbox(d: str) -> dict:
    """Conservative bbox from an SVG path's raw coordinate numbers.

    Good enough for mermaid's own generated paths (edges/arrowheads); it
    over-estimates slightly for curves since it treats control points as if
    they were on the path, which only ever makes the bbox a bit generous.
    """
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*(?:[eE]-?\d+)?", d or "")]
    xs, ys = nums[0::2], nums[1::2]
    if not xs:
        return {"x": 0, "y": 0, "width": 0, "height": 0}
    return {"x": min(xs), "y": min(ys), "width": max(xs) - min(xs), "height": max(ys) - min(ys)}


# ── Engine ───────────────────────────────────────────────────────────────────

class Engine:
    """
    One Engine = one QuickJS context with mermaid.js loaded, pinned to one
    dedicated worker thread. Reused across many renders (loading mermaid.js
    itself, ~6MB of source, is the expensive part — do it once).
    """

    def __init__(self) -> None:
        self._executor: Optional[ThreadPoolExecutor] = None
        self._ctx: Optional[quickjs.Context] = None
        self._measurer: Optional[_TextMeasurer] = None
        self._render_count = 0
        self._lock = threading.Lock()

    # -- lifecycle ------------------------------------------------------------

    def start(self) -> None:
        if self._executor is not None:
            return
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mmdc-engine")
        self._executor.submit(self._init_context).result()

    def close(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
            self._ctx = None
            self._measurer = None

    @property
    def started(self) -> bool:
        return self._executor is not None

    # -- worker-thread-only methods ---------------------------------------

    def _init_context(self) -> None:
        self._measurer = _TextMeasurer()
        ctx = quickjs.Context()
        ctx.set_memory_limit(512 * 1024 * 1024)
        # NOTE: no ctx.set_time_limit() — quickjs forbids calling back into
        # Python (needed constantly for text measurement) while a time limit
        # is active. Runaway scripts are bounded instead by the job-pump cap.

        ctx.add_callable("__log_raw", lambda s: print(f"[mmdc/js] {s}", file=sys.stderr))
        ctx.add_callable(
            "__measureText_raw",
            lambda t, s, f, w, st: self._measurer.width(t, s, f, w, st),
        )
        ctx.add_callable(
            "__measureTextFull_raw",
            lambda t, s, f, w, st: json.dumps(self._measurer.full(t, s, f, w, st)),
        )
        ctx.add_callable("__pathBBox_raw", lambda d: json.dumps(_path_bbox(d)))

        ctx.eval(
            "globalThis.__log = (s) => __log_raw(s);\n"
            "globalThis.__measureText = (t,s,f,w,st) => __measureText_raw(t,s,f,w,st);\n"
            "globalThis.__measureTextFull = (t,s,f,w,st) => JSON.parse(__measureTextFull_raw(t,s,f,w,st));\n"
            "globalThis.__pathBBox = (d) => JSON.parse(__pathBBox_raw(d));\n"
        )

        ctx.eval(_DOM_SHIM_JS.read_text(encoding="utf-8"))
        ctx.eval(_MERMAID_JS.read_text(encoding="utf-8"))
        ctx.eval(
            "globalThis.mermaid = (globalThis.__esbuild_esm_mermaid_nm.mermaid.default"
            " || globalThis.__esbuild_esm_mermaid_nm.mermaid);"
        )
        self._ctx = ctx

    def _pump_jobs(self) -> None:
        assert self._ctx is not None
        for _ in range(_RENDER_TIMEOUT_JOBS):
            try:
                if not self._ctx.execute_pending_job():
                    return
            except StopIteration:
                return

    def _render_svg_sync(self, code: str, theme: str, config: Optional[dict], css: Optional[str]) -> str:
        assert self._ctx is not None
        ctx = self._ctx
        self._render_count += 1
        render_id = f"gd{self._render_count}"

        base_config = {"startOnLoad": False, "theme": theme or "default",
                        "flowchart": {"htmlLabels": False}, "htmlLabels": False}
        if config:
            base_config.update(config)

        ctx.eval("__resetDocument();")
        ctx.set("__config", json.dumps(base_config))
        ctx.eval("mermaid.initialize(JSON.parse(__config));")

        if css:
            ctx.set("__css", css)
            ctx.eval(
                "(function(){"
                "  var el = document.getElementById('mmdc-css') || document.createElement('style');"
                "  el.setAttribute('id', 'mmdc-css');"
                "  el.textContent = __css;"
                "  document.head.appendChild(el);"
                "})();"
            )

        ctx.set("__code", code)
        ctx.set("__renderId", render_id)
        ctx.eval(
            "globalThis.__renderResult = null;\n"
            "globalThis.__renderError = null;\n"
            "mermaid.render(__renderId, __code)\n"
            "  .then(r => { globalThis.__renderResult = r.svg; })\n"
            "  .catch(e => { globalThis.__renderError = (e && e.name ? e.name+': '+e.message : String(e)); });\n"
        )
        self._pump_jobs()

        err = ctx.eval("globalThis.__renderError")
        if err:
            raise MermaidRenderError(str(err))
        svg = ctx.eval("globalThis.__renderResult")
        if not svg:
            raise MermaidRenderError("mermaid.render() produced no output (unknown error)")
        return str(svg)

    # -- public, thread-safe entry point ---------------------------------------

    def render_svg(self, code: str, theme: str, config: Optional[dict], css: Optional[str]) -> str:
        if self._executor is None:
            raise RuntimeError("Engine is not started.")
        return self._executor.submit(self._render_svg_sync, code, theme, config, css).result()
