var page = require('webpage').create();
var fs = require('fs');
var system = require('system');

page.settings.webSecurityEnabled = false;
page.settings.localToRemoteUrlAccessEnabled = true;

if (system.args.length < 3) {
    system.stderr.write("ERROR: Usage: phantomjs render.js input.mermaid output.svg\n");
    system.stderr.write("       If input.mermaid is '-', read from stdin.\n");
    phantom.exit(1);
}

var inputFile = system.args[1];
var outputFile = system.args[2];

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

    if (outputFile === "-") {
        // Write SVG to stdout
        system.stdout.write(svg);
    } else {
        fs.write(outputFile, svg, 'w');
    }
    phantom.exit(0);
});
