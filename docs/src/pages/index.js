import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="A Python tool for converting Mermaid diagrams to SVG, PNG, and PDF">
      <div className="hero hero--primary">
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className="row">
            <div className="col">
              <a
                className="button button--secondary button--lg"
                href="/docs/intro">
                Get Started - 5 min ⏱️
              </a>
            </div>
            <div className="col">
              <a
                className="button button--outline button--secondary button--lg"
                href="/docs/interactive-editor">
                Try Interactive Editor 🎨
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="container margin-vert--xl">
        <div className="row">
          <div className="col col--4">
            <h2>Easy to Use</h2>
            <p>Convert Mermaid diagrams to SVG, PNG, and PDF with simple commands or Python API.</p>
          </div>
          <div className="col col--4">
            <h2>Multiple Formats</h2>
            <p>Support for SVG, PNG, and PDF output formats with customizable dimensions and styling.</p>
          </div>
          <div className="col col--4">
            <h2>Full Control</h2>
            <p>Configure timeouts, dimensions, resolution, background colors, and CSS styling.</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}