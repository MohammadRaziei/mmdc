import argparse
import sys
import logging
from pathlib import Path
from . import MermaidConverter

def main():
    parser = argparse.ArgumentParser(
        description="Convert mermaid diagrams to SVG using PhantomJS (phasma)"
    )
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input mermaid file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output SVG file")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    converter = MermaidConverter(timeout=args.timeout)
    
    success = converter.convert(args.input, args.output)
    if success:
        logging.info(f"Successfully converted to {args.output}")
        sys.exit(0)
    else:
        logging.error("Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
