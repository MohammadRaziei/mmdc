"""Tests for mermaidx.engines.v8_engine's subprocess-based memory safety.

mindmap diagrams schedule an internal animation loop that never stops on
its own (see v8_engine.py's module docstring) -- py_mini_racer has no way
to interrupt it in-process, so the V8 isolate that gets stuck running it
lives in a child *process* instead of a thread: on timeout, that process is
killed outright (SIGKILL) and the OS reclaims 100% of its memory
immediately, unconditionally. These tests use a short render_timeout_ms to
exercise that path quickly rather than waiting out the real 8s default.
"""

from __future__ import annotations

import os
import time

import psutil
import pytest

pytest.importorskip("py_mini_racer")

from mermaidx.engines.v8_engine import Engine, MermaidRenderError  # noqa: E402

MINDMAP = "mindmap\n  root((mindmap))\n    Origins\n      Long history\n"
FLOWCHART = "flowchart TD\nA-->B"


@pytest.fixture
def engine():
    eng = Engine(render_timeout_ms=3000)  # short, just to exercise the path quickly
    eng.start()
    yield eng
    eng.close()


def _total_rss_mb(pid: int) -> float:
    """RSS of the given process plus all of its children (the V8 child
    process isn't the test process itself)."""
    proc = psutil.Process(pid)
    total = proc.memory_info().rss
    for child in proc.children(recursive=True):
        try:
            total += child.memory_info().rss
        except psutil.NoSuchProcess:
            pass
    return total / 1024 / 1024


def test_timed_out_render_raises_and_engine_recovers(engine):
    with pytest.raises(MermaidRenderError, match="killed"):
        engine.render_svg(MINDMAP, "default", None, None)
    # the engine replaced its killed child process -- a normal render works right after
    svg = engine.render_svg(FLOWCHART, "default", None, None)
    assert svg.startswith("<svg")


def test_killed_render_does_not_leak_memory(engine):
    """The regression this whole module exists to catch: an earlier,
    thread-based version of this engine leaked ~140-160MB *every single
    time* a render timed out, since an abandoned thread's V8 isolate could
    never be reclaimed. A killed child *process* must not show that
    pattern -- total memory should stay flat across repeated timeouts."""
    pid = os.getpid()

    for _ in range(3):
        with pytest.raises(MermaidRenderError, match="killed"):
            engine.render_svg(MINDMAP, "default", None, None)
        time.sleep(0.5)  # let the OS finish reaping the killed child

    rss_after_first_batch = _total_rss_mb(pid)

    for _ in range(3):
        with pytest.raises(MermaidRenderError, match="killed"):
            engine.render_svg(MINDMAP, "default", None, None)
        time.sleep(0.5)

    rss_after_second_batch = _total_rss_mb(pid)

    # generous tolerance (not a byte-exact check) -- the point is "flat", not "growing by ~150MB x 3"
    assert rss_after_second_batch < rss_after_first_batch + 50, (
        f"memory grew from {rss_after_first_batch:.1f}MB to {rss_after_second_batch:.1f}MB "
        "across a second batch of timeouts -- looks like a leak is back"
    )


def test_normal_render_matches_quickjs_output():
    """Sanity check that the subprocess architecture didn't change what
    gets rendered -- byte-identical to QuickJS, same as before."""
    from mermaidx.engines.quickjs_engine import Engine as QuickJSEngine

    qjs = QuickJSEngine()
    qjs.start()
    try:
        expected = qjs.render_svg(FLOWCHART, "default", None, None)
    finally:
        qjs.close()

    v8 = Engine()
    v8.start()
    try:
        actual = v8.render_svg(FLOWCHART, "default", None, None)
    finally:
        v8.close()

    assert actual == expected
