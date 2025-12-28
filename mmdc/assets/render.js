var page = require('webpage').create();
var fs = require('fs');
var system = require('system');

page.settings.webSecurityEnabled = false;
page.settings.localToRemoteUrlAccessEnabled = true;

// Parse command line arguments with optional flags
var inputFile = null;
var output = null;
var css = null;
var width = null;
var height = null;
var resolution = 96;
var background = null;

for (var i = 1; i < system.args.length; i++) {
    var arg = system.args[i];
    if (arg === '--css' && ++i < system.args.length) {
        css = system.args[i];
        // i already incremented
    } else if (arg === '--width' && ++i < system.args.length) {
        width = parseInt(system.args[i]);
        if (isNaN(width)) width = null;
    } else if (arg === '--height' && ++i < system.args.length) {
        height = parseInt(system.args[i]);
        if (isNaN(height)) height = null;
    } else if (arg === '--resolution' && ++i < system.args.length) {
        resolution = parseInt(system.args[i]);
        if (isNaN(resolution)) resolution = 96;
    } else if (arg === '--background' && ++i < system.args.length) {
        background = system.args[i];
    } else if (arg === '--help') {
        system.stderr.write("Usage: phantomjs render.js input.mermaid output [--css CSS] [--width W] [--height H] [--resolution R] [--background COLOR]\n");
        system.stderr.write("       output: 'svg', 'png', or 'pdf' for stdout, or filename with .svg/.png/.pdf extension\n");
        phantom.exit(0);
    } else {
        // positional arguments: input and output
        if (inputFile === null) {
            inputFile = arg;
        } else if (output === null) {
            output = arg;
        } else {
            system.stderr.write("ERROR: Unexpected argument: " + arg + "\n");
            phantom.exit(1);
        }
    }
}

if (inputFile === null || output === null) {
    system.stderr.write("ERROR: Missing required arguments. Usage: phantomjs render.js input.mermaid output [--css CSS] [--width W] [--height H] [--resolution R] [--background COLOR]\n");
    phantom.exit(1);
}

// Helper to parse integer or null if 0/empty/NaN
function parseOptionalInt(val) {
    if (val === undefined || val === null || val === '') return null;
    var num = parseInt(val);
    if (isNaN(num) || num === 0) return null;
    return num;
}

// Convert width/height to null if 0
width = parseOptionalInt(width);
height = parseOptionalInt(height);
resolution = parseOptionalInt(resolution) || 96;

var mermaidCode;
if (inputFile === "-") {
    // Read from stdin
    mermaidCode = system.stdin.read();
    if (!mermaidCode) {
        system.stderr.write("ERROR: No input provided via stdin\n");
        phantom.exit(1);
    }
} else {
    try {
        mermaidCode = fs.read(inputFile);
    } catch (e) {
        system.stderr.write("ERROR: Unable to read input file: " + e.toString() + "\n");
        phantom.exit(1);
    }
}

page.open('render.html', function (status) {
    if (status !== 'success') {
        system.stderr.write("ERROR: Failed to load page\n");
        phantom.exit(1);
    }

    // Inject CSS if provided
    if (css) {
        page.evaluate(function(cssText) {
            var style = document.createElement('style');
            style.type = 'text/css';
            style.appendChild(document.createTextNode(cssText));
            document.head.appendChild(style);
        }, css);
    }

    var svg = page.evaluate(function (code) {
        return window.renderMermaidSync(code);
    }, mermaidCode);

    if (!svg) {
        system.stderr.write("ERROR: SVG generation failed\n");
        phantom.exit(1);
    }

    // Determine output type from output string
    var type;
    if (output === 'svg' || output === 'png' || output === 'pdf') {
        type = output;
    } else {
        var outputExt = output.split('.').pop().toLowerCase();
        if (outputExt === 'svg' || outputExt === 'png' || outputExt === 'pdf') {
            type = outputExt;
        } else {
            type = 'svg'; // default
        }
    }
    
    // Determine if we should write to stdout
    var writeToStdout = (output === 'svg' || output === 'png' || output === 'pdf');
    
    if (type === 'svg') {
        if (writeToStdout) {
            // Write SVG to stdout
            system.stdout.write(svg);
        } else {
            fs.write(output, svg, 'w');
        }
        phantom.exit(0);
    } else if (type === 'png' || type === 'pdf') {
        // Helper function to render to PNG or PDF
        function renderToRaster(format) {
            // Inject SVG into page for rendering
            page.evaluate(function(svgContent, bgColor) {
                // Clear any existing content
                document.body.innerHTML = '';
                // Remove any margin/padding
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                // Apply background color if specified
                if (bgColor && bgColor !== 'transparent' && bgColor !== 'none') {
                    document.body.style.backgroundColor = bgColor;
                }
                // Create div for SVG
                var div = document.createElement('div');
                div.innerHTML = svgContent;
                div.style.margin = '0';
                div.style.padding = '0';
                document.body.appendChild(div);
            }, svg, background);
            
            // Wait a bit for rendering
            setTimeout(function() {
                // Get SVG dimensions
                var dimensions = page.evaluate(function() {
                    var svgElem = document.querySelector('svg');
                    if (!svgElem) return null;
                    var bbox = svgElem.getBBox();
                    return {
                        width: Math.ceil(bbox.width),
                        height: Math.ceil(bbox.height),
                        x: Math.floor(bbox.x),
                        y: Math.floor(bbox.y)
                    };
                });
                
                if (!dimensions) {
                    system.stderr.write("ERROR: Could not get SVG dimensions\n");
                    phantom.exit(1);
                }
                
                // Apply width/height if provided
                var finalWidth = (width !== null) ? width : dimensions.width;
                var finalHeight = (height !== null) ? height : dimensions.height;
                
                // Calculate scale if width/height provided but only one dimension
                if (width !== null && height === null) {
                    finalHeight = Math.round(dimensions.height * (width / dimensions.width));
                } else if (height !== null && width === null) {
                    finalWidth = Math.round(dimensions.width * (height / dimensions.height));
                }
                
                // Apply resolution (DPI) scaling
                var scale = resolution / 96;
                finalWidth = Math.round(finalWidth * scale);
                finalHeight = Math.round(finalHeight * scale);
                
                // Set viewport and clipRect
                page.viewportSize = {
                    width: finalWidth,
                    height: finalHeight
                };
                page.clipRect = {
                    top: 0,
                    left: 0,
                    width: finalWidth,
                    height: finalHeight
                };
                
                // Set zoom factor for resolution
                page.zoomFactor = scale;
                
                if (writeToStdout) {
                    // Raster output to stdout is not supported
                    system.stderr.write("ERROR: " + format.toUpperCase() + " output to stdout not supported. Please specify a filename with ." + format + " extension.\n");
                    phantom.exit(1);
                } else {
                    if (format === 'pdf') {
                        page.render(output, { format: 'pdf' });
                    } else {
                        page.render(output);
                    }
                }
                phantom.exit(0);
            }, 100);
        }
        
        // Call helper with appropriate format
        renderToRaster(type);
    } else {
        system.stderr.write("ERROR: Unsupported output type. Use 'svg', 'png', or 'pdf'\n");
        phantom.exit(1);
    }
});
