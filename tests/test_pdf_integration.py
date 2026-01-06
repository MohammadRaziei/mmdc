#!/usr/bin/env python3
"""
Integration tests for PDF conversion in mmdc.
"""
import pytest
import tempfile

from pathlib import Path
from mmdc import MermaidConverter


class TestPDFIntegration:
    """Integration tests for PDF conversion."""
    
    def test_to_pdf_function(self):
        """Test the to_pdf method directly."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        pdf_bytes = converter.to_pdf(mermaid_code)
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        # PDF magic bytes
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_with_css(self):
        """Test PDF conversion with CSS styling."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        pdf_bytes = converter.to_pdf(mermaid_code, css=css)
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_with_background(self):
        """Test PDF conversion with background color."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        pdf_bytes = converter.to_pdf(mermaid_code, background='#00FF00')
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_with_dimensions(self):
        """Test PDF conversion with custom width/height."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        pdf_bytes = converter.to_pdf(mermaid_code, width=400, height=300)
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_with_resolution(self):
        """Test PDF conversion with custom resolution."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        pdf_bytes = converter.to_pdf(mermaid_code, resolution=150)
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_with_all_options(self):
        """Test PDF conversion with all optional parameters."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        pdf_bytes = converter.to_pdf(
            mermaid_code,
            width=500,
            height=400,
            resolution=150,
            background='#FFFFFF',
            css=css
        )
        
        assert pdf_bytes is not None, "PDF bytes should not be None"
        assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
        assert pdf_bytes.startswith(b'%PDF'), "Should be valid PDF"
    
    def test_to_pdf_file_output(self):
        """Test PDF conversion with file output."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            converter.to_pdf(mermaid_code, output_file=output_path)
            
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            # Check PDF magic bytes
            with open(output_path, 'rb') as pdf_file:
                magic = pdf_file.read(8)
                assert magic.startswith(b'%PDF'), "Should be valid PDF"
            
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_to_pdf_with_css_file_output(self):
        """Test PDF conversion with CSS and file output."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            converter.to_pdf(mermaid_code, output_file=output_path, css=css)
            
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            with open(output_path, 'rb') as pdf_file:
                magic = pdf_file.read(8)
                assert magic.startswith(b'%PDF'), "Should be valid PDF"
            
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_convert_pdf(self):
        """Test convert method for PDF files."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)

        try:
            success = converter.convert(input_path, output_path)

            assert success is True, "Conversion should succeed"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'rb') as pdf_file:
                magic = pdf_file.read(8)
                assert magic.startswith(b'%PDF'), "Should be valid PDF"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()

    def test_convert_pdf_with_options(self):
        """Test convert method for PDF files with additional options."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)

        # Create temporary config and CSS files
        config_content = '{"theme": "dark"}'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)

        css_content = ".node { fill: #00ff00; }"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(css_content)
            css_path = Path(f.name)

        try:
            # Read the input file content
            input_content = input_path.read_text()
            result = converter.convert(
                input_content, output_path,
                theme="forest",
                background="#ffffff",
                width=1200,
                height=900,
                config_file=config_path,
                css_file=css_path,
                scale=1.5
            )

            assert result is None, "Conversion should succeed and return None when output file specified"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'rb') as pdf_file:
                magic = pdf_file.read(8)
                assert magic.startswith(b'%PDF'), "Should be valid PDF"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            if config_path.exists():
                config_path.unlink()
            if css_path.exists():
                css_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
