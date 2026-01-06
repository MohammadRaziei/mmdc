---
sidebar_position: 3
---

# Usage

## Command Line Interface

Convert a Mermaid file to SVG:

```bash
mmdc --input diagram.mermaid --output diagram.svg
```

Convert to PNG or PDF (output format determined by file extension):

```bash
# Convert to PNG
mmdc --input diagram.mermaid --output diagram.png

# Convert to PDF
mmdc --input diagram.mermaid --output diagram.pdf
```

With custom timeout (in seconds):

```bash
mmdc --input diagram.mermaid --output diagram.svg --timeout 60
```

Enable verbose logging:

```bash
mmdc --input diagram.mermaid --output diagram.svg --verbose
```

## Python API

### Basic Conversion

```python
from mmdc import MermaidConverter
from pathlib import Path

converter = MermaidConverter()

# Convert a diagram (output format determined by file extension)
success = converter.convert(
    input_file=Path("diagram.mermaid"),
    output_file=Path("diagram.svg")  # or .png or .pdf
)

if success:
    print("Conversion successful!")
else:
    print("Conversion failed.")
```

### Direct Format Conversion

```python
from mmdc import MermaidConverter
from pathlib import Path

converter = MermaidConverter()

# Convert to SVG string
svg_content = converter.to_svg("graph TD\n  A --> B")

# Convert to SVG file
converter.to_svg("graph TD\n  A --> B", output_file=Path("output.svg"))

# Convert to PNG bytes
png_bytes = converter.to_png("graph TD\n  A --> B")

# Convert to PNG file
converter.to_png("graph TD\n  A --> B", output_file=Path("output.png"))

# Convert to PDF bytes
pdf_bytes = converter.to_pdf("graph TD\n  A --> B")

# Convert to PDF file
converter.to_pdf("graph TD\n  A --> B", output_file=Path("output.pdf"))
```

### Advanced Options

```python
from mmdc import MermaidConverter

converter = MermaidConverter(timeout=60)  # Set timeout to 60 seconds (default is 30)

# Convert with custom styling and dimensions
converter.to_svg(
    input="graph TD\n  A --> B",
    output_file=Path("styled.svg"),
    css=".node { fill: #ff0000; }",
    theme="dark",  # Use dark theme
    background="#f0f0f0"  # Light gray background
)

# Convert PNG with custom dimensions and background
converter.to_png(
    input="graph TD\n  A --> B",
    output_file=Path("custom.png"),
    width=800,
    height=600,
    resolution=150,  # Higher resolution (DPI)
    background="#FFFFFF",
    css=".node { fill: #00ff00; }",
    theme="forest"  # Forest theme
)

# Convert PDF with custom resolution
converter.to_pdf(
    input="graph TD\n  A --> B",
    output_file=Path("high_res.pdf"),
    resolution=150,
    background="#000000",
    theme="dark"
)

# Convert using a config file and CSS file
config_file = Path("mermaid-config.json")
css_file = Path("custom-styles.css")
converter.to_svg(
    input="graph TD\n  A --> B",
    output_file=Path("configured.svg"),
    config_file=config_file,
    css_file=css_file
)
```

### Using Different Input Types

The converter methods accept different types of input:

```python
from mmdc import MermaidConverter
from pathlib import Path

converter = MermaidConverter()

# String input
svg_content = converter.to_svg("graph TD\n  A --> B")

# Path to a file containing the diagram
input_file = Path("diagram.mermaid")
svg_content = converter.to_svg(input_file.read_text())

# File-like object
with open("diagram.mermaid", "r") as f:
    svg_content = converter.to_svg(f)
```