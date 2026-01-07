# mmdc - Mermaid Diagram Converter

[![PyPI - Version](https://img.shields.io/pypi/v/mmdc.svg)](https://pypi.org/project/mmdc)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mmdc.svg)](https://pypi.org/project/mmdc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/MohammadRaziei/mmdc/actions/workflows/test.yml/badge.svg)](https://github.com/MohammadRaziei/mmdc/actions/workflows/test.yml)


<div align="center">
<img src="https://raw.githubusercontent.com/MohammadRaziei/mmdc/master/docs/static/img/logo.svg" width="150pt">
</div>

A Python tool for converting Mermaid diagrams to SVG, PNG, and PDF using PhantomJS (via [phasma](https://pypi.org/project/phasma/)). Perfect for automating diagram generation in documentation pipelines, CI/CD workflows, and static site generation.

## Features

- **Multiple Output Formats**: Convert Mermaid diagrams to SVG, PNG, and PDF
- **Multiple Diagram Types**: Supports flowcharts, sequence diagrams, Gantt charts, pie charts, and more
- **Command Line & Python API**: Use as a CLI tool or import as a Python library
- **Configurable Options**: Set custom timeouts, dimensions, resolution, background colors, and CSS styling
- **Comprehensive Testing**: Fully tested with parametrized tests covering various scenarios
- **Logging Support**: Built-in logging with verbose mode for debugging

## Installation

### From PyPI

```bash
pip install mmdc
```

### From Source

```bash
git clone https://github.com/MohammadRaziei/mmdc.git
cd mmdc
pip install -e .
```

## Usage

### Command Line Interface

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

### Python API

#### Basic Conversion

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

#### Direct Format Conversion

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

#### Advanced Options

```python
from mmdc import MermaidConverter

converter = MermaidConverter(timeout=60)  # Set timeout to 60 seconds

# Convert with custom styling and dimensions
converter.to_svg(
    input="graph TD\n  A --> B",
    output_file=Path("styled.svg"),
    css=".node { fill: #ff0000; }"
)

# Convert PNG with custom dimensions and background
converter.to_png(
    input="graph TD\n  A --> B",
    output_file=Path("custom.png"),
    width=800,
    height=600,
    background="#FFFFFF",
    css=".node { fill: #00ff00; }"
)

# Convert PDF with custom resolution
converter.to_pdf(
    input="graph TD\n  A --> B",
    output_file=Path("high_res.pdf"),
    resolution=150,
    background="#000000"
)
```

## Examples

### Basic Flowchart

Create a file `flowchart.mermaid`:

```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

Convert to different formats:

```bash
# To SVG
mmdc --input flowchart.mermaid --output flowchart.svg

# To PNG
mmdc --input flowchart.mermaid --output flowchart.png

# To PDF
mmdc --input flowchart.mermaid --output flowchart.pdf
```

### Sequence Diagram

Create a file `sequence.mermaid`:

```
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!
```

Convert to different formats:

```bash
mmdc --input sequence.mermaid --output sequence.png
```

### Gantt Chart

Create a file `gantt.mermaid`:

```
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2014-01-12, 12d
    another task     :24d
```

Convert with custom timeout for complex diagrams:

```bash
mmdc --input gantt.mermaid --output gantt.pdf --timeout 60
```

## Testing

The project includes comprehensive tests using pytest. Run the tests with:

```bash
pytest tests/ -v
```

Or use the hatch test environment:

```bash
hatch run test
```

### Test Coverage

Tests cover:
- Various Mermaid diagram types (flowcharts, sequence diagrams, Gantt charts, pie charts)
- Different output formats (SVG, PNG, PDF)
- Different timeout values
- Error cases (non-existent files, empty diagrams)
- Special characters in diagrams
- Custom styling with CSS
- Custom dimensions and background colors
- Integration with the command line interface

## How It Works

`mmdc` uses [PhantomJS](https://phantomjs.org/) via the [phasma](https://pypi.org/project/phasma/) Python package to render Mermaid diagrams. The process:

1. **Template Preparation**: Uses embedded HTML/JavaScript templates in `mmdc/assets/`
2. **Diagram Rendering**: PhantomJS loads the Mermaid library and renders the diagram
3. **Output Generation**: The rendered diagram is converted to the requested format (SVG, PNG, or PDF)

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/MohammadRaziei/mmdc.git
   cd mmdc
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code passes all tests and follows the project's coding standards.

## License

`mmdc` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Acknowledgments

- [Mermaid.js](https://mermaid-js.github.io/) for the amazing diagramming library
- [PhantomJS](https://phantomjs.org/) for headless browser capabilities
- [phasma](https://pypi.org/project/phasma/) for the PhantomJS Python integration

## Support

If you encounter any problems or have questions, please [open an issue](https://github.com/MohammadRaziei/mmdc/issues) on GitHub.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/MohammadRaziei">Mohammad Raziei</a>
</div>
