import React, { useState, useEffect } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const MermaidEditor = () => {
  const [diagramCode, setDiagramCode] = useState(`graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E`);

  const [renderedDiagram, setRenderedDiagram] = useState('');

  // Load Mermaid from CDN
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://raw.githubusercontent.com/MohammadRaziei/mmdc/master/mmdc/assets/mermaid.min.js';
    script.async = true;
    script.onload = () => {
      // Initialize Mermaid
      if (window.mermaid) {
        window.mermaid.initialize({ 
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose'
        });
        renderDiagram();
      }
    };
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  const renderDiagram = () => {
    if (window.mermaid) {
      try {
        window.mermaid.render('mermaid-diagram', diagramCode, (svgCode) => {
          setRenderedDiagram(svgCode);
        });
      } catch (error) {
        setRenderedDiagram(`<p style="color: red;">Error rendering diagram: ${error.message}</p>`);
      }
    }
  };

  const handleRender = () => {
    renderDiagram();
  };

  const handleCodeChange = (e) => {
    setDiagramCode(e.target.value);
  };

  // Auto-render when diagram code changes
  useEffect(() => {
    const timeoutId = setTimeout(renderDiagram, 500);
    return () => clearTimeout(timeoutId);
  }, [diagramCode]);

  return (
    <div className="mermaid-container">
      <div>
        <label htmlFor="mermaid-editor"><strong>Mermaid Diagram Code:</strong></label>
        <textarea
          id="mermaid-editor"
          className="mermaid-editor"
          value={diagramCode}
          onChange={handleCodeChange}
          rows={10}
        />
        <button 
          id="render-btn" 
          className="button button--primary"
          onClick={handleRender}
        >
          Render Diagram
        </button>
      </div>
      <div 
        id="mermaid-preview" 
        className="mermaid-preview"
        dangerouslySetInnerHTML={{ __html: renderedDiagram }}
      />
    </div>
  );
};

const MermaidEditorWrapper = () => {
  return (
    <BrowserOnly fallback={<div>Loading Mermaid Editor...</div>}>
      {() => <MermaidEditor />}
    </BrowserOnly>
  );
};

export default MermaidEditorWrapper;