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
    """Integration tests that actually convert Mermaid to SVG."""
    
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
        converter = MermaidConverter()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path, timeout=30)
            
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
    
    @pytest.mark.parametrize("timeout", [1, 5, 10, 30])
    def test_conversion_with_different_timeouts(self, timeout):
        """Test conversion with different timeout values."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path, timeout=timeout)
            
            # Should succeed even with short timeouts for simple diagram
            assert success is True, f"Conversion should succeed with timeout={timeout}"
            assert output_path.exists(), f"Output file should exist with timeout={timeout}"
            assert output_path.stat().st_size > 0, f"Output file should not be empty with timeout={timeout}"
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    def test_invalid_input_file(self):
        """Test conversion with non-existent input file."""
        converter = MermaidConverter()
        
        input_path = Path("/non/existent/file.mermaid")
        output_path = Path(tempfile.mktemp(suffix='.svg'))
        
        success = converter.convert(input_path, output_path, timeout=10)
        
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
            success = converter.convert(input_path, output_path, timeout=30)
            
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
            success = converter.convert(input_path, output_path, timeout=30)
            
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
