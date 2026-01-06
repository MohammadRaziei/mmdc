---
sidebar_position: 1
---

# Introduction

`mmdc` is a Python tool for converting Mermaid diagrams to SVG, PNG, and PDF using PhantomJS (via [phasma](https://pypi.org/project/phasma/)). Perfect for automating diagram generation in documentation pipelines, CI/CD workflows, and static site generation.

## Features

- **Multiple Output Formats**: Convert Mermaid diagrams to SVG, PNG, and PDF
- **Multiple Diagram Types**: Supports flowcharts, sequence diagrams, Gantt charts, pie charts, and more
- **Command Line & Python API**: Use as a CLI tool or import as a Python library
- **Configurable Options**: Set custom timeouts, dimensions, resolution, background colors, and CSS styling
- **Comprehensive Testing**: Fully tested with parametrized tests covering various scenarios
- **Logging Support**: Built-in logging with verbose mode for debugging

## How It Works

`mmdc` uses [PhantomJS](https://phantomjs.org/) via the [phasma](https://pypi.org/project/phasma/) Python package to render Mermaid diagrams. The process:

1. **Template Preparation**: Uses embedded HTML/JavaScript templates in `mmdc/assets/`
2. **Diagram Rendering**: PhantomJS loads the Mermaid library and renders the diagram
3. **Output Generation**: The rendered diagram is converted to the requested format (SVG, PNG, or PDF)
4. **Cleanup**: Temporary files are cleaned up automatically

## Support

If you encounter any problems or have questions, please [open an issue](https://github.com/MohammadRaziei/mmdc/issues) on GitHub.