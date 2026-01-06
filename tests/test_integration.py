#!/usr/bin/env python3
"""
Integration tests for mmdc.
These tests actually run the conversion process.
"""
import pytest
import tempfile

from pathlib import Path
import xml.etree.ElementTree as ET

from mmdc import MermaidConverter


def is_valid_svg(content: str) -> bool:
    """Check if content is valid SVG."""
    try:
        # Try to parse as XML
        root = ET.fromstring(content)
        return root.tag.endswith('svg')
    except ET.ParseError:
        return False


class TestIntegration:
    """General integration tests for mmdc."""
    
    def test_convert_svg(self):
        """Test convert method for SVG files."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)

        try:
            # Read the input file content
            input_content = input_path.read_text()
            result = converter.convert(input_content, output_path)

            assert result is None, "Conversion should succeed and return None when output file specified"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()

            assert '<svg' in svg_content, "Output should contain SVG tag"
            assert is_valid_svg(svg_content), "Output should be valid SVG"

        finally:
            if input_path.exists():
                input_path.unlink()
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
            # Read the input file content
            input_content = input_path.read_text()
            result = converter.convert(input_content, output_path)

            assert result is None, "Conversion should succeed and return None when output file specified"
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
            # Read the input file content
            input_content = input_path.read_text()
            result = converter.convert(input_content, output_path)

            assert result is None, "PDF conversion should succeed and return None when output file specified"
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
    
    def test_invalid_output_format(self):
        """Test conversion with invalid output format."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = Path(f.name)

        try:
            success = converter.convert(input_path, output_path)

            assert success is False, "Conversion should fail for invalid format"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()

    def test_convert_with_themes(self):
        """Test convert method with different themes."""
        for theme in ["default", "forest", "dark", "neutral"]:
            converter = MermaidConverter()

            mermaid_code = "graph TD\n  A --> B"

            with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
                f.write(mermaid_code)
                input_path = Path(f.name)

            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
                output_path = Path(f.name)

            try:
                success = converter.convert(input_path, output_path, theme=theme)

                assert success is True, f"Conversion should succeed for theme {theme}"
                assert output_path.exists(), "Output file should exist"
                assert output_path.stat().st_size > 0, "Output file should not be empty"

                with open(output_path, 'r') as svg_file:
                    svg_content = svg_file.read()

                assert '<svg' in svg_content, "Output should contain SVG tag"
                assert is_valid_svg(svg_content), "Output should be valid SVG"

            finally:
                if input_path.exists():
                    input_path.unlink()
                if output_path.exists():
                    output_path.unlink()

    def test_convert_with_backgrounds(self):
        """Test convert method with different backgrounds."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)

        try:
            success = converter.convert(input_path, output_path, background="#ff0000")

            assert success is True, "Conversion should succeed with custom background"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()

            assert '<svg' in svg_content, "Output should contain SVG tag"
            assert is_valid_svg(svg_content), "Output should be valid SVG"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()

    def test_convert_with_config_file(self):
        """Test convert method with config file."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)

        # Create a temporary config file
        config_content = '{"theme": "dark", "flowchart": {"useMaxWidth": false}}'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)

        try:
            success = converter.convert(input_path, output_path, config_file=config_path)

            assert success is True, "Conversion should succeed with config file"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()

            assert '<svg' in svg_content, "Output should contain SVG tag"
            assert is_valid_svg(svg_content), "Output should be valid SVG"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            if config_path.exists():
                config_path.unlink()

    def test_convert_with_css_file(self):
        """Test convert method with CSS file."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)

        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)

        # Create a temporary CSS file
        css_content = ".node { fill: #00ff00; stroke: #0000ff; }"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(css_content)
            css_path = Path(f.name)

        try:
            success = converter.convert(input_path, output_path, css_file=css_path)

            assert success is True, "Conversion should succeed with CSS file"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()

            assert '<svg' in svg_content, "Output should contain SVG tag"
            assert is_valid_svg(svg_content), "Output should be valid SVG"

        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            if css_path.exists():
                css_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
