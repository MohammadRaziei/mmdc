#!/usr/bin/env python3
"""
Mermaid Diagram Converter using PhantomJS (phasma) with runtime template replacement.
Supports SVG, PNG, PDF output.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Union, TextIO

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
    
    def to_svg(self, input: Union[str, TextIO], output_file: Optional[Path] = None,
               css: Optional[str] = None) -> Optional[str]:
        """
        Convert Mermaid diagram (text or file-like object) to SVG string or file.
        
        Args:
            input: Mermaid code as string, or a file-like object with .read() method
            output_file: Optional path to save SVG file. If None, returns string.
            
        Returns:
            SVG content as string if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """
        # Determine if input is a string or file-like object
        if isinstance(input, str):
            # String
            mermaid_code = input
        else:
            # File-like object
            mermaid_code = input.read()
        
        # Build command arguments for render.js
        args = [str(self.render_js), "-", "svg"]
        if css is not None:
            args.append("--css")
            args.append(css)
        
        # Run phantomjs via phasma driver, read from stdin ("-") and output to stdout ("svg")
        result = self.driver.exec(
            args,
            capture_output=True,
            timeout=self.timeout,
            ssl=False,
            cwd=self.assets_dir,
            input=mermaid_code.encode()
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
    
    def _render_to_file(self, input: Union[str, TextIO], output_file: Optional[Path], 
                        file_extension: str, width: Optional[int] = None,
                        height: Optional[int] = None, resolution: int = 96,
                        background: Optional[str] = None, css: Optional[str] = None) -> Optional[bytes]:
        """
        Internal helper to render Mermaid to a file (PNG or PDF).
        
        Args:
            input: Mermaid code as string or file-like object
            output_file: Optional path to save file. If None, uses temp file.
            file_extension: '.png' or '.pdf'
            width: Output width in pixels
            height: Output height in pixels
            resolution: DPI resolution
            background: Background color
            css: Custom CSS
            
        Returns:
            File bytes if output_file is None, otherwise None
        """
        import tempfile
        
        # Determine if input is a string or file-like object
        if isinstance(input, str):
            mermaid_code = input
        else:
            mermaid_code = input.read()
        
        # If output_file is None, use a temporary file
        temp_file = None
        if output_file is None:
            temp_file = Path(tempfile.mktemp(suffix=file_extension))
            output_target = temp_file
        else:
            output_target = output_file
        
        # Build command arguments for render.js with named flags
        args = [str(self.render_js), "-", str(output_target)]
        
        # Add CSS if specified
        if css is not None:
            args.append("--css")
            args.append(css)
        
        # Add width if specified
        if width is not None:
            args.append("--width")
            args.append(str(width))
        
        # Add height if specified
        if height is not None:
            args.append("--height")
            args.append(str(height))
        
        # Add resolution if not default
        if resolution != 96:
            args.append("--resolution")
            args.append(str(resolution))
        
        # Add background if specified
        if background is not None:
            args.append("--background")
            args.append(background)
        
        # Run phantomjs via phasma driver
        result = self.driver.exec(
            args,
            capture_output=True,
            timeout=self.timeout,
            ssl=False,
            cwd=self.assets_dir,
            input=mermaid_code.encode()
        )

        stdout = result.stdout if result.stdout else b""
        stderr = result.stderr.decode() if result.stderr else ""
        
        self.logger.debug(f"stdout length: {len(stdout)} bytes")
        self.logger.debug(f"stderr: {stderr}")
        
        # Check for errors
        if "ERROR:" in stderr or "ReferenceError" in stderr:
            raise RuntimeError(f"PhantomJS error: {stderr}")
        
        if result.returncode != 0:
            error = stderr if stderr else "Unknown error"
            raise RuntimeError(f"PhantomJS exited with code {result.returncode}: {error}")
        
        # If we used a temp file, read it and delete
        if temp_file:
            if temp_file.exists():
                file_bytes = temp_file.read_bytes()
                temp_file.unlink()
                return file_bytes
            else:
                raise RuntimeError(f"{file_extension.upper()} file was not created")
        else:
            # output_file was provided, no bytes to return
            return None
    
    def to_png(self, input: Union[str, TextIO], output_file: Optional[Path] = None,
               scale: float = 1.0, width: Optional[int] = None,
               height: Optional[int] = None, resolution: int = 96,
               background: Optional[str] = None, css: Optional[str] = None) -> Optional[bytes]:
        """
        Convert Mermaid diagram (text or file-like) to PNG bytes or file using PhantomJS.
        
        Args:
            input: Mermaid code as string, or a file-like object with .read() method
            output_file: Optional path to save PNG file. If None, returns bytes.
            scale: Scale factor for output (default 1.0) - overridden by width/height
            width: Output width in pixels (overrides scale)
            height: Output height in pixels (overrides scale)
            resolution: DPI resolution (default 96)
            
        Returns:
            PNG bytes if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """
        # Note: scale parameter is kept for backward compatibility but overridden by width/height
        return self._render_to_file(
            input=input,
            output_file=output_file,
            file_extension='.png',
            width=width,
            height=height,
            resolution=resolution,
            background=background,
            css=css
        )
    
    def to_pdf(self, input: Union[str, TextIO], output_file: Optional[Path] = None,
               scale: float = 1.0, width: Optional[int] = None,
               height: Optional[int] = None, resolution: int = 96,
               background: Optional[str] = None, css: Optional[str] = None) -> Optional[bytes]:
        """
        Convert Mermaid diagram (text or file-like) to PDF bytes or file using PhantomJS.
        
        Args:
            input: Mermaid code as string, or a file-like object with .read() method
            output_file: Optional path to save PDF file. If None, returns bytes.
            scale: Scale factor for output (default 1.0) - overridden by width/height
            width: Output width in pixels (overrides scale)
            height: Output height in pixels (overrides scale)
            resolution: DPI resolution (default 96)
            background: Background color (e.g., '#FFFFFF', 'transparent')
            css: Custom CSS to inject
            
        Returns:
            PDF bytes if output_file is None, otherwise None
            
        Raises:
            RuntimeError: If conversion fails
        """
        # Note: scale parameter is kept for backward compatibility but overridden by width/height
        return self._render_to_file(
            input=input,
            output_file=output_file,
            file_extension='.pdf',
            width=width,
            height=height,
            resolution=resolution,
            background=background,
            css=css
        )
    
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
            # Read Mermaid code from file
            mermaid_code = input_file.read_text()
            
            if output_ext == ".svg":
                svg_content = self.to_svg(mermaid_code)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(svg_content)
                self.logger.debug(f"SVG written to {output_file}")
                return True
            elif output_ext == ".png":
                self.to_png(mermaid_code, output_file=output_file)
                self.logger.debug(f"PNG written to {output_file}")
                return True
            elif output_ext == ".pdf":
                self.to_pdf(mermaid_code, output_file=output_file)
                self.logger.debug(f"PDF written to {output_file}")
                return True
            else:
                self.logger.error(f"Unsupported output format: {output_ext}. Use .svg, .png, or .pdf")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            return False
