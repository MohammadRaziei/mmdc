// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['installation', 'usage'],
    },
    {
      type: 'category',
      label: 'Advanced Usage',
      items: ['api', 'examples'],
    },
    'interactive-editor',
  ],
};

module.exports = sidebars;