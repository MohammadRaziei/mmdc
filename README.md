# mmdc - Mermaid Diagram Converter

[![PyPI - Version](https://img.shields.io/pypi/v/mmdc.svg)](https://pypi.org/project/mmdc)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mmdc.svg)](https://pypi.org/project/mmdc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/MohammadRaziei/mmdc/actions/workflows/test.yml/badge.svg)](https://github.com/MohammadRaziei/mmdc/actions/workflows/test.yml)

A Python tool for converting Mermaid diagrams to SVG using PhantomJS (via [phasma](https://pypi.org/project/phasma/)). Perfect for automating diagram generation in documentation pipelines, CI/CD workflows, and static site generation.

## Features

- **Convert Mermaid to SVG**: Transform `.mermaid` files into high-quality SVG images
- **Multiple Diagram Types**: Supports flowcharts, sequence diagrams, Gantt charts, pie charts, and more
- **Command Line & Python API**: Use as a CLI tool or import as a Python library
- **Configurable Timeout**: Set custom timeouts for complex diagrams
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

With custom timeout (in seconds):

```bash
mmdc --input diagram.mermaid --output diagram.svg --timeout 60
```

Enable verbose logging:

```bash
mmdc --input diagram.mermaid --output diagram.svg --verbose
```

### Python API

```python
from mmdc import MermaidConverter
from pathlib import Path

converter = MermaidConverter()

# Convert a diagram
success = converter.convert(
    input_file=Path("diagram.mermaid"),
    output_file=Path("diagram.svg"),
    timeout=30  # optional, default is 30 seconds
)

if success:
    print("Conversion successful!")
else:
    print("Conversion failed.")
```

## Examples

### Basic Flowchart

Create a file `flowchart.mermaid`:

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

Convert to SVG:

```bash
mmdc --input flowchart.mermaid --output flowchart.svg
```

### Sequence Diagram

Create a file `sequence.mermaid`:

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!
```

Convert to SVG:

```bash
mmdc --input sequence.mermaid --output sequence.svg
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
- Different timeout values
- Error cases (non-existent files, empty diagrams)
- Special characters in diagrams
- Integration with the command line interface

## How It Works

`mmdc` uses [PhantomJS](https://phantomjs.org/) via the [phasma](https://pypi.org/project/phasma/) Python package to render Mermaid diagrams. The process:

1. **Template Preparation**: Uses embedded HTML/JavaScript templates in `mmdc/assets/`
2. **Diagram Rendering**: PhantomJS loads the Mermaid library and renders the diagram
3. **SVG Extraction**: The rendered SVG is extracted and saved to the output file
4. **Cleanup**: Temporary files are cleaned up automatically

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

### Code Quality

The project uses several tools for maintaining code quality:

- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing with coverage

Run all code quality checks:

```bash
hatch run lint:all
```

Format code:

```bash
hatch run lint:fmt
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
