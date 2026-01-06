---
sidebar_position: 1
---

# API Reference

## MermaidConverter Class

The main class for converting Mermaid diagrams.

### Constructor

```python
MermaidConverter(timeout: int = 30)
```

- `timeout` (int, optional): Timeout in seconds for diagram rendering. Default is 30 seconds.

### Methods

#### convert()

Converts a Mermaid diagram to the specified output format based on file extension.

```python
def convert(self,
            input: Union[str, TextIO, Path],
            output_file: Optional[Path] = None,
            theme: Optional[str] = None,
            background: Optional[str] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            config_file: Optional[Path] = None,
            css_file: Optional[Path] = None,
            scale: float = 1.0) -> Optional[Union[str, bytes]]
```

- `input` (Union[str, TextIO, Path]): Mermaid diagram as string, file-like object, or Path to a file
- `output_file` (Optional[Path]): Path for the output file (format determined by extension: .svg, .png, .pdf)
- `theme` (Optional[str]): Theme for the diagram (default, forest, dark, neutral)
- `background` (Optional[str]): Background color (default: white)
- `width` (Optional[int]): Width of the diagram in pixels
- `height` (Optional[int]): Height of the diagram in pixels
- `config_file` (Optional[Path]): Path to JSON config file for Mermaid
- `css_file` (Optional[Path]): Path to CSS file to apply to the diagram
- `scale` (float): Scale factor for output (default 1.0)
- Returns: Content as string (for SVG) or bytes (for PNG/PDF) if `output_file` is None, otherwise None

#### to_svg()

Converts a Mermaid diagram to SVG.

```python
def to_svg(self,
           input: Union[str, TextIO],
           output_file: Optional[Path] = None,
           css: Optional[str] = None,
           theme: Optional[str] = None,
           background: Optional[str] = None,
           width: Optional[int] = None,
           height: Optional[int] = None,
           config_file: Optional[Path] = None,
           css_file: Optional[Path] = None) -> Optional[str]
```

- `input` (Union[str, TextIO]): Mermaid diagram as string or file-like object
- `output_file` (Optional[Path]): Path to save the SVG file
- `css` (Optional[str]): Inline CSS to apply to the diagram
- `theme` (Optional[str]): Theme for the diagram (default, forest, dark, neutral)
- `background` (Optional[str]): Background color (default: white)
- `width` (Optional[int]): Width of the diagram in pixels
- `height` (Optional[int]): Height of the diagram in pixels
- `config_file` (Optional[Path]): Path to JSON config file for Mermaid
- `css_file` (Optional[Path]): Path to CSS file to apply to the diagram
- Returns: SVG content as string if `output_file` is None, otherwise None

#### to_png()

Converts a Mermaid diagram to PNG.

```python
def to_png(self,
           input: Union[str, TextIO],
           output_file: Optional[Path] = None,
           scale: float = 1.0,
           width: Optional[int] = None,
           height: Optional[int] = None,
           resolution: int = 96,
           background: Optional[str] = None,
           css: Optional[str] = None,
           theme: Optional[str] = None,
           config_file: Optional[Path] = None,
           css_file: Optional[Path] = None) -> Optional[bytes]
```

- `input` (Union[str, TextIO]): Mermaid diagram as string or file-like object
- `output_file` (Optional[Path]): Path to save the PNG file
- `scale` (float): Scale factor for output (default 1.0)
- `width` (Optional[int]): Output width in pixels (overrides scale)
- `height` (Optional[int]): Output height in pixels (overrides scale)
- `resolution` (int): DPI resolution (default 96)
- `background` (Optional[str]): Background color (default: white)
- `css` (Optional[str]): Inline CSS to apply to the diagram
- `theme` (Optional[str]): Theme for the diagram (default, forest, dark, neutral)
- `config_file` (Optional[Path]): Path to JSON config file for Mermaid
- `css_file` (Optional[Path]): Path to CSS file to apply to the diagram
- Returns: PNG bytes if `output_file` is None, otherwise None

#### to_pdf()

Converts a Mermaid diagram to PDF.

```python
def to_pdf(self,
           input: Union[str, TextIO],
           output_file: Optional[Path] = None,
           scale: float = 1.0,
           width: Optional[int] = None,
           height: Optional[int] = None,
           resolution: int = 96,
           background: Optional[str] = None,
           css: Optional[str] = None,
           theme: Optional[str] = None,
           config_file: Optional[Path] = None,
           css_file: Optional[Path] = None) -> Optional[bytes]
```

- `input` (Union[str, TextIO]): Mermaid diagram as string or file-like object
- `output_file` (Optional[Path]): Path to save the PDF file
- `scale` (float): Scale factor for output (default 1.0)
- `width` (Optional[int]): Output width in pixels (overrides scale)
- `height` (Optional[int]): Output height in pixels (overrides scale)
- `resolution` (int): DPI resolution (default 96)
- `background` (Optional[str]): Background color (e.g., '#FFFFFF', 'transparent')
- `css` (Optional[str]): Custom CSS to inject
- `theme` (Optional[str]): Theme for the diagram (default, forest, dark, neutral)
- `config_file` (Optional[Path]): Path to JSON config file for Mermaid
- `css_file` (Optional[Path]): Path to CSS file to apply to the diagram
- Returns: PDF bytes if `output_file` is None, otherwise None

### Supported Themes

- `default`: Standard Mermaid theme
- `forest`: Green-themed style
- `dark`: Dark-themed style
- `neutral`: Neutral color scheme

### Supported Output Formats

- `.svg`: Scalable Vector Graphics
- `.png`: Portable Network Graphics
- `.pdf`: Portable Document Format