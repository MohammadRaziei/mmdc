import argparse
import sys
from pathlib import Path
from . import MermaidConverter

def main():
    parser = argparse.ArgumentParser(
        description="Convert mermaid diagrams to SVG using PhantomJS (phasma)"
    )
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input mermaid file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output SVG file")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    converter = MermaidConverter()
    
    success = converter.convert(args.input, args.output, args.timeout)
    if success:
        print(f"Successfully converted to {args.output}", file=sys.stderr)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()