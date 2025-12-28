#!/usr/bin/env python3
"""
Integration tests for PNG conversion in mmdc.
"""
import pytest
import tempfile

from pathlib import Path
from mmdc import MermaidConverter


class TestPNGIntegration:
    """Integration tests for PNG conversion."""
    
    def test_to_png_function(self):
        """Test the to_png method directly."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        png_bytes = converter.to_png(mermaid_code)
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        # PNG magic bytes
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_with_css(self):
        """Test PNG conversion with CSS styling."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        png_bytes = converter.to_png(mermaid_code, css=css)
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_with_background(self):
        """Test PNG conversion with background color."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        png_bytes = converter.to_png(mermaid_code, background='#00FF00')
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_with_dimensions(self):
        """Test PNG conversion with custom width/height."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        png_bytes = converter.to_png(mermaid_code, width=400, height=300)
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_with_resolution(self):
        """Test PNG conversion with custom resolution."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        png_bytes = converter.to_png(mermaid_code, resolution=150)
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_with_all_options(self):
        """Test PNG conversion with all optional parameters."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        png_bytes = converter.to_png(
            mermaid_code,
            width=500,
            height=400,
            resolution=150,
            background='#FFFFFF',
            css=css
        )
        
        assert png_bytes is not None, "PNG bytes should not be None"
        assert len(png_bytes) > 0, "PNG bytes should not be empty"
        assert png_bytes.startswith(b'\x89PNG'), "Should be valid PNG"
    
    def test_to_png_file_output(self):
        """Test PNG conversion with file output."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            converter.to_png(mermaid_code, output_file=output_path)
            
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            # Check PNG magic bytes
            with open(output_path, 'rb') as png_file:
                magic = png_file.read(8)
                assert magic.startswith(b'\x89PNG'), "Should be valid PNG"
            
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_to_png_with_css_file_output(self):
        """Test PNG conversion with CSS and file output."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            converter.to_png(mermaid_code, output_file=output_path, css=css)
            
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            with open(output_path, 'rb') as png_file:
                magic = png_file.read(8)
                assert magic.startswith(b'\x89PNG'), "Should be valid PNG"
            
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_convert_png(self):
        """Test convert method for PNG files."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path)
            
            assert success is True, "Conversion should succeed"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            with open(output_path, 'rb') as png_file:
                magic = png_file.read(8)
                assert magic.startswith(b'\x89PNG'), "Should be valid PNG"
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
