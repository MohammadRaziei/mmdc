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
    
    def test_basic_conversion(self):
        """Test converting a basic Mermaid diagram."""
        converter = MermaidConverter()
        
        # Create a simple Mermaid diagram
        mermaid_code = """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path, timeout=30)
            
            assert success is True, "Conversion should succeed"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            # Check that it's valid SVG
            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()
            
            assert '<svg' in svg_content, "Output should contain SVG tag"
            assert 'graph TD' not in svg_content, "Output should not contain Mermaid code"
            
            # Basic validation
            assert is_valid_svg(svg_content), "Output should be valid SVG"
            
        finally:
            # Cleanup
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    def test_sequence_diagram(self):
        """Test converting a sequence diagram."""
        converter = MermaidConverter()
        
        mermaid_code = """sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            success = converter.convert(input_path, output_path, timeout=30)
            
            assert success is True, "Conversion should succeed"
            assert output_path.exists(), "Output file should exist"
            assert output_path.stat().st_size > 0, "Output file should not be empty"
            
            with open(output_path, 'r') as svg_file:
                svg_content = svg_file.read()
            
            assert '<svg' in svg_content, "Output should contain SVG tag"
            
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
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    def test_timeout(self):
        """Test conversion with very short timeout (should still work for simple diagram)."""
        converter = MermaidConverter()
        
        mermaid_code = "graph TD\n  A --> B"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
            f.write(mermaid_code)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            # Very short timeout, but should still work for simple diagram
            success = converter.convert(input_path, output_path, timeout=5)
            
            assert success is True, "Conversion should succeed with short timeout"
            assert output_path.exists(), "Output file should exist"
            
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
