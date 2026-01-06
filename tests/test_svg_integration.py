#!/usr/bin/env python3
"""
Integration tests for SVG conversion in mmdc.
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


class TestSVGIntegration:
    """Integration tests for SVG conversion."""
    
    @pytest.mark.parametrize("mermaid_code,description", [
        ("""graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E""", "basic flowchart"),
        ("""sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!""", "sequence diagram"),
        ("""graph LR
    A[Square] --> B(Round)
    B --> C{Decision}
    C --> D[Result]""", "left-right flowchart"),
        ("""pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15""", "pie chart"),
        ("""gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2014-01-12, 12d
    another task     :24d""", "gantt chart"),
    ])
    def test_mermaid_conversion(self, mermaid_code, description):
        """Test converting various Mermaid diagrams to SVG."""
        converter = MermaidConverter(timeout=30)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path)
            
            assert success is True, f"Conversion should succeed for {description}"
            assert output_path.exists(), f"Output file should exist for {description}"
            assert output_path.stat().st_size > 0, f"Output file should not be empty for {description}"
            
            # Check that it's valid SVG
            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()
            
            assert '<svg' in svg_content, f"Output should contain SVG tag for {description}"
            # Basic validation
            assert is_valid_svg(svg_content), f"Output should be valid SVG for {description}"
            
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    def test_invalid_input_file(self):
        """Test conversion with non-existent input file."""
        converter = MermaidConverter(timeout=10)
        
        input_path = Path("/non/existent/file.mermaid")
        output_path = Path(tempfile.mktemp(suffix='.svg'))
        
        success = converter.convert(input_path, output_path)
        
        assert success is False, "Conversion should fail for non-existent file"
    
    def test_empty_mermaid(self):
        """Test converting empty Mermaid code."""
        converter = MermaidConverter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write("")
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path)
            
            # Empty Mermaid might fail or produce empty SVG
            # We just check that it doesn't crash
            if success:
                assert output_path.exists(), "Output file should exist"
                # If it produces output, it should be valid SVG
                with open(output_path, 'r') as svg_file:
                    svg_content = svg_file.read()
                if svg_content.strip():
                    assert '<svg' in svg_content, "Output should contain SVG tag"
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    @pytest.mark.parametrize("special_chars", [
        "graph TD\n  A[Test & < > \" '] --> B",
        "graph TD\n  A[Line1\nLine2] --> B",
        "graph TD\n  A[Special chars: © ® €] --> B",
    ])
    def test_mermaid_with_special_characters(self, special_chars):
        """Test converting Mermaid with special characters."""
        converter = MermaidConverter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False, encoding='utf-8') as f:
            f.write(special_chars)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path)
            
            # Conversion might succeed or fail depending on PhantomJS handling
            # We just check it doesn't crash
            if success:
                assert output_path.exists(), "Output file should exist"
                assert output_path.stat().st_size > 0, "Output file should not be empty"
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    def test_to_svg_function(self):
        """Test the to_svg method directly."""
        converter = MermaidConverter()
        
        # Direct string input
        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code)
        
        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"
    
    def test_to_svg_with_invalid_file(self):
        """Test to_svg with invalid input (empty string)."""
        converter = MermaidConverter(timeout=10)
        
        # Empty string should raise RuntimeError
        with pytest.raises(RuntimeError):
            converter.to_svg("")
    
    def test_to_svg_with_css(self):
        """Test SVG conversion with CSS styling."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"
        svg = converter.to_svg(mermaid_code, css=css)
        
        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert 'style' in svg.lower(), "SVG should contain style tag from CSS"
        assert is_valid_svg(svg), "SVG should be valid"
    
    def test_to_svg_with_css_file_output(self):
        """Test SVG conversion with CSS styling and file output."""
        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"
        css = ".node { fill: #ff0000; }"

        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)

        try:
            converter.to_svg(mermaid_code, output_file=output_path, css=css)

            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"

            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()

            assert '<svg' in svg_content, "SVG should contain SVG tag"
            assert 'style' in svg_content.lower(), "SVG should contain style tag from CSS"
            assert is_valid_svg(svg_content), "SVG should be valid"

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_to_svg_with_theme(self):
        """Test SVG conversion with different themes."""
        converter = MermaidConverter(theme="dark")

        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code, theme="forest")

        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"

    def test_to_svg_with_background(self):
        """Test SVG conversion with custom background."""
        converter = MermaidConverter(background="transparent")

        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code, background="#000000")

        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"

    def test_to_svg_with_dimensions(self):
        """Test SVG conversion with custom dimensions."""
        converter = MermaidConverter(width=1000, height=800)

        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code, width=1200, height=900)

        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"

    def test_to_svg_with_config_file(self):
        """Test SVG conversion with config file."""
        # Create a temporary config file
        config_content = '{"theme": "dark", "flowchart": {"useMaxWidth": false}}'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)

        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code, config_file=config_path)

        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"

        # Cleanup
        if config_path.exists():
            config_path.unlink()

    def test_to_svg_with_css_file_param(self):
        """Test SVG conversion with CSS file parameter."""
        # Create a temporary CSS file
        css_content = ".node { fill: #00ff00; stroke: #0000ff; }"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(css_content)
            css_path = Path(f.name)

        converter = MermaidConverter()

        mermaid_code = "graph TD\n  A --> B"
        svg = converter.to_svg(mermaid_code, css_file=css_path)

        assert svg is not None, "SVG should not be None"
        assert len(svg) > 0, "SVG should not be empty"
        assert '<svg' in svg, "SVG should contain SVG tag"
        assert is_valid_svg(svg), "SVG should be valid"

        # Cleanup
        if css_path.exists():
            css_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
