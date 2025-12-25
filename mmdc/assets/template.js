var page = require('webpage').create();
var fs = require('fs');
var system = require('system');

page.settings.webSecurityEnabled = false;
page.settings.localToRemoteUrlAccessEnabled = true;

if (system.args.length < 3) {
    console.log("Usage: phantomjs render.js input.mermaid output.svg");
    phantom.exit(1);
}

var inputFile = system.args[1];
var outputFile = system.args[2];

var mermaidCode = fs.read(inputFile);

page.open('PATH_TO_RENDER_HTML', function (status) {
    if (status !== 'success') {
        console.log('Failed to load page');
        phantom.exit(1);
    }

    var svg = page.evaluate(function (code) {
        return window.renderMermaidSync(code);
    }, mermaidCode);

    if (!svg) {
        console.log("SVG generation failed");
        phantom.exit(1);
    }

    fs.write(outputFile, svg, 'w');
    phantom.exit(0);
});
