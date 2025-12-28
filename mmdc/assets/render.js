var page = require('webpage').create();
var fs = require('fs');
var system = require('system');

page.settings.webSecurityEnabled = false;
page.settings.localToRemoteUrlAccessEnabled = true;

if (system.args.length < 3) {
    system.stderr.write("ERROR: Usage: phantomjs render.js input.mermaid output [width] [height] [resolution] [background]\n");
    system.stderr.write("       output: 'svg' or 'png' for stdout, or filename with .svg/.png extension\n");
    system.stderr.write("       width, height, resolution: optional for PNG output (use 0 for unspecified)\n");
    system.stderr.write("       background: optional background color (e.g., '#FFFFFF' or 'white'), default transparent\n");
    phantom.exit(1);
}

var inputFile = system.args[1];
var output = system.args[2]; // can be 'svg', 'png', or filename
// Helper to parse integer or null if 0/empty/NaN
function parseOptionalInt(val) {
    if (val === undefined || val === null || val === '') return null;
    var num = parseInt(val);
    if (isNaN(num) || num === 0) return null;
    return num;
}

var width = system.args.length > 3 ? parseOptionalInt(system.args[3]) : null;
var height = system.args.length > 4 ? parseOptionalInt(system.args[4]) : null;
var resolution = system.args.length > 5 ? parseOptionalInt(system.args[5]) : 96; // DPI
var background = system.args.length > 6 ? system.args[6] : null; // background color

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

    var svg = page.evaluate(function (code) {
        return window.renderMermaidSync(code);
    }, mermaidCode);

    if (!svg) {
        system.stderr.write("ERROR: SVG generation failed\n");
        phantom.exit(1);
    }

    // Determine output type from output string
    var type;
    if (output === 'svg' || output === 'png') {
        type = output;
    } else {
        var outputExt = output.split('.').pop().toLowerCase();
        if (outputExt === 'svg' || outputExt === 'png') {
            type = outputExt;
        } else {
            type = 'svg'; // default
        }
    }
    
    // Determine if we should write to stdout
    var writeToStdout = (output === 'svg' || output === 'png');
    
    if (type === 'svg') {
        if (writeToStdout) {
            // Write SVG to stdout
            system.stdout.write(svg);
        } else {
            fs.write(output, svg, 'w');
        }
        phantom.exit(0);
    } else if (type === 'png') {
        // Inject SVG into page for rendering
        page.evaluate(function(svgContent, bgColor) {
            var div = document.createElement('div');
            div.innerHTML = svgContent;
            document.body.appendChild(div);
            // Remove any margin/padding
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            div.style.margin = '0';
            div.style.padding = '0';
            // Apply background color if specified
            if (bgColor && bgColor !== 'transparent' && bgColor !== 'none') {
                document.body.style.backgroundColor = bgColor;
            }
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
                // PNG output to stdout is not supported
                system.stderr.write("ERROR: PNG output to stdout not supported. Please specify a filename with .png extension.\n");
                phantom.exit(1);
            } else {
                page.render(output);
            }
            phantom.exit(0);
        }, 100);
    } else {
        system.stderr.write("ERROR: Unsupported output type. Use 'svg' or 'png'\n");
        phantom.exit(1);
    }
});
