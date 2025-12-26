#!/usr/bin/env python3
"""
Mermaid Diagram Converter using PhantomJS (phasma) with runtime template replacement.
"""

import sys
import tempfile
import os
from pathlib import Path

from phasma.driver import Driver


class MermaidConverter:
    def __init__(self):
        # Determine assets directory relative to this file
        self.assets_dir = (Path(__file__).parent / "assets").resolve()
        self.template_js = self.assets_dir / "template.js"
        self.template_html = self.assets_dir / "template.html"
        self.mermaid_js = self.assets_dir / "mermaid.min.js"
        
        if not self.template_js.exists():
            raise FileNotFoundError(f"template.js not found at {self.template_js}")
        if not self.template_html.exists():
            raise FileNotFoundError(f"template.html not found at {self.template_html}")
        if not self.mermaid_js.exists():
            raise FileNotFoundError(f"mermaid.min.js not found at {self.mermaid_js}")
        
        self.driver = Driver()
    
    def convert(self, input_file: Path, output_file: Path, timeout: int = 30) -> bool:
        """
        Convert Mermaid diagram to SVG.
        Returns True on success.
        """
        # Ensure absolute paths
        input_file = input_file.absolute()
        output_file = output_file.absolute()
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="mmdc_"))
        print(temp_dir)
        render_html_path = temp_dir / "render.html"
        render_js_path = temp_dir / "render.js"
        
        try:
            with open(self.template_js, 'r') as f:
                js_content = f.read()

            js_content = js_content.replace('PATH_TO_RENDER_HTML', render_html_path.as_posix())

            with open(render_js_path, 'w') as f:
                f.write(js_content)


            
            with open(self.template_html, 'r') as f:
                html_content = f.read()
            
            html_content = html_content.replace('PATH_TO_MERMAID', self.mermaid_js.as_uri())
            
            with open(render_html_path, 'w') as f:
                f.write(html_content)
            
            # Change to temp directory so relative paths work
            original_cwd = Path.cwd()
            os.chdir(temp_dir)
            
            # Run phantomjs via phasma driver
            result = self.driver.exec(
                [str(render_js_path), str(input_file), str(output_file)],
                capture_output=True,
                timeout=timeout,
                ssl=False,
            )
            
            if result.returncode != 0:
                error = result.stderr.decode() if result.stderr else "Unknown error"
                print(f"Error: {error}", file=sys.stderr)
                return False
            
            if not output_file.exists():
                print(f"Error: Output file not created", file=sys.stderr)
                return False
            
            return True
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        finally:
            # Restore original directory
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            # Cleanup temp directory
            import shutil
            # shutil.rmtree(temp_dir, ignore_errors=True)



