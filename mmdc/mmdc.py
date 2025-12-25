#!/usr/bin/env python3
"""
Mermaid Diagram Converter (mmdc) - Phasma/PhantomJS version
Note: Current mermaid.js versions may not be compatible with PhantomJS.
"""

import argparse
import sys
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from phasma.driver import Driver
import phasma




def main():
    parser = argparse.ArgumentParser(
        description="Convert mermaid diagrams to SVG using PhantomJS (phasma)",
        epilog="Note: Current mermaid.js versions may not be compatible with PhantomJS."
    )
    
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("-i", "--input", type=Path, help="Input mermaid file")
    input_group.add_argument("-c", "--code", type=str, help="Mermaid code as string")
    
    parser.add_argument("-o", "--output", type=Path, help="Output SVG file")
    
    args = parser.parse_args()
    
    
    try:
        converter = MermaidConverter()
        success, message = converter.convert(args.input, args.output, args.code)
        
        if success:
            print(message, file=sys.stderr)
        else:
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
