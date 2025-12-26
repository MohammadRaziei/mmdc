#!/usr/bin/env python3
"""
Mermaid Diagram Converter using PhantomJS (phasma) with runtime template replacement.
"""

import sys
import tempfile
import os
import logging
from pathlib import Path

from phasma.driver import Driver


class MermaidConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Determine assets directory relative to this file
        self.assets_dir = (Path(__file__).parent / "assets").resolve()
        self.render_js = "render.js"
        self.render_html = "render.html"
        
        self.driver = Driver()
    
    def convert(self, input_file: Path, output_file: Path, timeout: int = 30) -> bool:
        """
        Convert Mermaid diagram to SVG.
        Returns True on success.
        """
        # Ensure absolute paths
        input_file = input_file.absolute()
        output_file = output_file.absolute()
        
        try:
            # Run phantomjs via phasma driver
            result = self.driver.exec(
                [str(self.render_js), str(input_file), str(output_file)],
                capture_output=True,
                timeout=timeout,
                ssl=False,
                cwd=self.assets_dir
            )

            if result.stdout: self.logger.debug(f"stdout: {result.stdout}")
            if result.stderr: self.logger.debug(f"stderr: {result.stderr}")
            
            if result.returncode != 0:
                error = result.stderr.decode() if result.stderr else "Unknown error"
                self.logger.error(f"Error: {error}")
                return False
            
            if not output_file.exists():
                self.logger.error("Output file not created")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            return False

