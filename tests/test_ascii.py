"""Tests for mmdc.render_ascii (backed by termaid, a core dependency)."""

from __future__ import annotations

import mmdc

SIMPLE = "graph LR\nA-->B"


def test_render_ascii_basic():
    art = mmdc.render_ascii(SIMPLE)
    assert isinstance(art, str)
    assert "A" in art and "B" in art


def test_render_ascii_use_ascii_option():
    art = mmdc.render_ascii(SIMPLE, use_ascii=True)
    # pure-ASCII mode shouldn't contain Unicode box-drawing characters
    assert not any(ch in art for ch in "┌┐└┘│─►")
