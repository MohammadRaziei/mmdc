# MMDC with Phasma

## Overview
MMDC (Mermaid Diagram Converter) uses Phasma (PhantomJS driver) to convert Mermaid diagrams to SVG and PNG without requiring Node.js or a full browser.

## Architecture

### Components
1. **Phasma**: Python wrapper for PhantomJS
2. **PhantomJS**: Headless WebKit browser (v2.1.1)
3. **Mermaid.js**: JavaScript diagramming library
4. **CairoSVG**: Python library for SVG to PNG conversion

### Flow
```
Mermaid Code → PhantomJS (via Phasma) → SVG → [CairoSVG] → PNG
```

## Implementation Details

### 1. Rendering with PhantomJS
- Load `mmdc/assets/mermaid.min.js` in PhantomJS
- Create HTML page with embedded Mermaid code
- Use PhantomJS to execute JavaScript and render diagram
- Extract SVG output from page


### 2. PNG Conversion with CairoSVG
```python
import cairosvg

def svg_to_png(svg_content: str, output_path: Path, width: int = 800, height: int = 600):
    cairosvg.svg2png(bytestring=svg_content.encode('utf-8'),
                     write_to=str(output_path),
                     output_width=width,
                     output_height=height)
```

## Current Issues and Solutions

### Issue 1: Mermaid.js Compatibility
- **Problem**: Modern mermaid.js versions use ES6+ features not supported by PhantomJS 2.1.1
- **Solution**: Use older mermaid.js version (v8.x) compatible with PhantomJS

### Issue 2: Optional Chaining Operator
- **Problem**: `mermaid_render.js` uses `?.` operator (ES2020)
- **Solution**: Replace with compatible syntax:
  ```javascript
  // Before: document.getElementById("output_svg")?.innerHTML
  // After: var elem = document.getElementById("output_svg"); return elem ? elem.innerHTML : null;
  ```

### Issue 3: Output Capture
- **Problem**: `driver.exec()` doesn't capture output by default
- **Solution**: Use `capture_output=True` parameter

## Setup Instructions

### 1. Install Dependencies
```bash
pip install phasma cairosvg
```

### 2. Ensure PhantomJS is Available
- Phasma includes PhantomJS binary
- No separate installation needed

### 3. Use Compatible Mermaid.js
- Place compatible mermaid.min.js in `mmdc/assets/`
- Recommended: mermaid.js v8.13.10 or earlier

## Usage Example

```bash
# Convert to SVG
python mmdc.py -i diagram.mermaid -o diagram.svg

# Convert to PNG
python mmdc.py -i diagram.mermaid -o diagram.png

# Convert to both
python mmdc.py -i diagram.mermaid -o diagram.svg diagram.png
```

## Advantages Over Original Implementation

1. **No Node.js Required**: Uses PhantomJS instead of Node
2. **No Full Browser**: Headless rendering without Chrome/Firefox
3. **Lightweight**: PhantomJS is lighter than full browser
4. **Python Native**: All Python stack, easier to maintain

## Limitations

1. **PhantomJS Limitations**: Older WebKit, limited ES6 support
2. **Mermaid Version**: Must use compatible mermaid.js version
3. **Performance**: Slower than modern headless Chrome

## Future Improvements

1. **Upgrade PhantomJS**: If newer PhantomJS version becomes available
2. **Alternative Renderers**: Consider other headless browsers
3. **Caching**: Cache rendered diagrams for performance
4. **Batch Processing**: Support multiple files at once
