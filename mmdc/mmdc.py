#!/usr/bin/env python3
"""
Mermaid Diagram Converter using PhantomJS (phasma) with runtime template replacement.
Supports SVG, PNG, PDF output.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from phasma.driver import Driver
# import cairosvg


class MermaidConverter:
    def __init__(self, timeout: int = 30):
        self.logger = logging.getLogger(__name__)
        # Determine assets directory relative to this file
        self.assets_dir = (Path(__file__).parent / "assets").resolve()
        self.render_js = "render.js"
        self.render_html = "render.html"
        self.timeout = timeout
        
        self.driver = Driver()
    
    def to_svg(self, input_file: Path, output_file: Optional[Path] = None) -> Optional[str]:
        """
        Convert Mermaid diagram file to SVG string or file.
        
        Args:
            input_file: Path to Mermaid file
            output_file: Optional path to save SVG file. If None, returns string.
            
        Returns:
            SVG content as string if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """
        # Ensure absolute path
        input_file = input_file.absolute()
        
        # Run phantomjs via phasma driver, output to stdout ("-")
        result = self.driver.exec(
            [str(self.render_js), str(input_file), "-"],
            capture_output=True,
            timeout=self.timeout,
            ssl=False,
            cwd=self.assets_dir
        )

        stdout = result.stdout.decode() if result.stdout else ""
        stderr = result.stderr.decode() if result.stderr else ""
        
        self.logger.debug(f"stdout length: {len(stdout)} chars")
        self.logger.debug(f"stderr: {stderr}")
        
        # Check for errors in stderr (errors are written to stderr)
        if "ERROR:" in stderr or "ReferenceError" in stderr:
            raise RuntimeError(f"PhantomJS error: {stderr}")
        
        if result.returncode != 0:
            error = stderr if stderr else "Unknown error"
            raise RuntimeError(f"PhantomJS exited with code {result.returncode}: {error}")
        
        # If stdout is empty but no error, something went wrong
        if not stdout.strip():
            raise RuntimeError("No SVG content generated")
        
        # Success: stdout contains SVG
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(stdout)
            self.logger.debug(f"SVG written to {output_file}")
            return None
        else:
            return stdout
    
    def to_png(self, input_file: Path, output_file: Optional[Path] = None, 
               scale: float = 1.0, width: Optional[int] = None, 
               height: Optional[int] = None) -> Optional[bytes]:
        """
        Convert Mermaid diagram file to PNG bytes or file.
        
        Args:
            input_file: Path to Mermaid file
            output_file: Optional path to save PNG file. If None, returns bytes.
            scale: Scale factor for output (default 1.0)
            width: Output width in pixels (overrides scale)
            height: Output height in pixels (overrides scale)
            
        Returns:
            PNG bytes if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """

        raise NotImplementedError

        # First get SVG
        # svg = self.to_svg(input_file).encode()
        
        # # Convert SVG to PNG
        # png_bytes = cairosvg.svg2png(bytestring=svg, output_width=width, output_height=height, scale=scale)
        
        # if output_file:
        #     output_file.parent.mkdir(parents=True, exist_ok=True)
        #     output_file.write_bytes(png_bytes)
        #     self.logger.debug(f"PNG written to {output_file}")
        #     return None
        # else:
        #     return png_bytes
    
    def to_pdf(self, input_file: Path, output_file: Optional[Path] = None,
               scale: float = 1.0, width: Optional[int] = None,
               height: Optional[int] = None) -> Optional[bytes]:
        """
        Convert Mermaid diagram file to PDF bytes or file.
        
        Args:
            input_file: Path to Mermaid file
            output_file: Optional path to save PDF file. If None, returns bytes.
            scale: Scale factor for output (default 1.0)
            width: Output width in pixels (overrides scale)
            height: Output height in pixels (overrides scale)
            
        Returns:
            PDF bytes if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """
        raise NotImplementedError

        # First get SVG
        # svg = self.to_svg(input_file).encode()
        
        # # Convert SVG to PDF
        # pdf_bytes = cairosvg.svg2pdf(bytestring=svg, output_width=width, output_height=height, scale=scale)
        
        # if output_file:
        #     output_file.parent.mkdir(parents=True, exist_ok=True)
        #     output_file.write_bytes(pdf_bytes)
        #     self.logger.debug(f"PDF written to {output_file}")
        #     return None
        # else:
        #     return pdf_bytes
    
    def convert(self, input_file: Path, output_file: Path) -> bool:
        """
        Convert Mermaid diagram to SVG, PNG, or PDF based on output file extension.
        Returns True on success.
        """
        # Ensure absolute paths
        input_file = input_file.absolute()
        output_file = output_file.absolute()
        
        output_ext = output_file.suffix.lower()
        
        try:
            if output_ext == ".svg":
                svg_content = self.to_svg(input_file)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(svg_content)
                self.logger.debug(f"SVG written to {output_file}")
                return True
            elif output_ext == ".png":
                self.to_png(input_file, output_file=output_file)
                self.logger.debug(f"PNG written to {output_file}")
                return True
            elif output_ext == ".pdf":
                self.to_pdf(input_file, output_file=output_file)
                self.logger.debug(f"PDF written to {output_file}")
                return True
            else:
                self.logger.error(f"Unsupported output format: {output_ext}. Use .svg, .png, or .pdf")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            return False
