"""
mmdc CLI — python -m mmdc

Convert Mermaid diagrams to SVG, PNG, or PDF. Fully synchronous: rendering
is CPU-bound (no browser process, no I/O to wait on), so there's no event
loop here at all -- one less thing to start up.

Examples:
    mmdc -i diagram.mermaid                    # SVG to stdout
    mmdc -i diagram.mermaid -o diagram.svg
    mmdc -i diagram.mermaid -o diagram.png -w 1200
    mmdc -i diagram.mermaid -o diagram.pdf --pdf-format A4
    cat diagram.mermaid | mmdc -i -
    mmdc --info
    mmdc --list-backends
    mmdc -i diagram.mermaid --backend merman -o diagram.svg
"""

import argparse
import json
import sys
from pathlib import Path

import mmdc
from mmdc.diagram import Diagram


def _get_version() -> str:
    try:
        import importlib.metadata
        return importlib.metadata.version("mmdc")
    except Exception:
        return "unknown"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mmdc",
        description="Convert Mermaid diagrams to SVG, PNG, or PDF — fully offline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  mmdc -i diagram.mermaid                         # SVG to stdout
  mmdc -i diagram.mermaid -o diagram.svg
  mmdc -i diagram.mermaid -o diagram.png -w 1200
  mmdc -i diagram.mermaid -o diagram.png --scale 2.0
  mmdc -i diagram.mermaid -o diagram.pdf
  mmdc -i diagram.mermaid -o diagram.pdf --pdf-format A4 --landscape
  mmdc -i diagram.mermaid -o diagram.svg --theme dark
  cat diagram.mermaid | mmdc -i -
  mmdc --info
  mmdc --list-backends
  mmdc -i diagram.mermaid --backend merman -o diagram.svg
        """,
    )

    parser.add_argument("--version", "-v", action="version", version=_get_version())
    parser.add_argument("--info", action="store_true",
                        help="Print Mermaid library version and exit")
    parser.add_argument("--list-backends", action="store_true",
                        help="List available rendering backends and exit")
    parser.add_argument("--backend", default=None, metavar="NAME",
                        help="Rendering backend to use (default: js). "
                             "See --list-backends for what's available.")
    parser.add_argument("-i", "--input", metavar="FILE",
                        help="Input Mermaid file, or '-' to read from stdin")
    parser.add_argument("-o", "--output", default=None, metavar="FILE",
                        help="Output file (.svg/.png/.pdf). Omit to write SVG to stdout.")
    parser.add_argument("-w", "--width", type=float, default=None, metavar="N",
                        help="Output width in pixels (PNG/PDF-fit)")
    parser.add_argument("-H", "--height", type=float, default=None, metavar="N",
                        help="Output height in pixels (PNG/PDF-fit)")
    parser.add_argument("--scale", type=float, default=None, metavar="N",
                        help="Size multiplier, used if -w/-H are omitted (e.g. 2.0)")
    parser.add_argument("-t", "--theme",
                        choices=["default", "forest", "dark", "neutral"],
                        default="default",
                        help="Mermaid theme (default: default)")
    parser.add_argument("-b", "--background", default=None, metavar="COLOR",
                        help="CSS background color (default: transparent)")
    parser.add_argument("-c", "--config", metavar="FILE",
                        help="JSON config file for Mermaid (backend='js' only)")
    parser.add_argument("--css", metavar="FILE",
                        help="CSS file to inject into the diagram (backend='js' only)")
    parser.add_argument("--pdf-format", default=None, metavar="FORMAT",
                        help="PDF paper format e.g. A4, Letter (default: fit to diagram)")
    parser.add_argument("--landscape", action="store_true",
                        help="Landscape orientation (PDF only)")
    parser.add_argument("--margin", default="0", metavar="MARGIN",
                        help="PDF margin e.g. '1cm' (default: 0)")

    return parser


def _read_source(input_arg: str) -> str:
    if input_arg == "-":
        return sys.stdin.read()
    return Path(input_arg).read_text(encoding="utf-8")


def _print_info(backend) -> None:
    import xml.etree.ElementTree as ET

    svg_str = mmdc.render("info", backend=backend).svg()
    root = ET.fromstring(svg_str)
    texts = [
        el.text.strip()
        for el in root.iter()
        if el.tag.split("}")[-1] == "text" and el.text and el.text.strip()
    ]
    print(" ".join(texts))


def _print_backends() -> None:
    available = mmdc.backends()
    for name in available:
        marker = " (default)" if name == "js" else ""
        print(f"{name}{marker}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    backend = args.backend or "js"

    if args.info:
        _print_info(backend)
        return

    if args.list_backends:
        _print_backends()
        return

    if not args.input:
        parser.error("the following arguments are required: -i/--input")

    source = _read_source(args.input)
    config = json.loads(Path(args.config).read_text(encoding="utf-8")) if args.config else None
    css = Path(args.css).read_text(encoding="utf-8") if args.css else None

    render_kwargs = {"theme": args.theme}
    if backend == "js":
        render_kwargs.update(config=config, css=css)
    elif config or css:
        print(f"warning: --config/--css are ignored for backend={backend!r} (only 'js' supports them)",
              file=sys.stderr)

    d = mmdc.render(source, backend=args.backend, **render_kwargs)

    if args.output is None:
        sys.stdout.buffer.write(d.svg().encode("utf-8"))
        return

    output = Path(args.output)
    raster_kwargs = dict(width=args.width, height=args.height, scale=args.scale, background=args.background)
    suffix = output.suffix.lower()

    if suffix == ".pdf":
        d.save(str(output), **raster_kwargs, pdf_format=args.pdf_format,
               pdf_landscape=args.landscape, pdf_margin=args.margin)
    else:
        d.save(str(output), **raster_kwargs)

    print(f"saved to {output}  ({output.stat().st_size:,} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
