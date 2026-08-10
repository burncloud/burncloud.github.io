const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
module.exports = {
  title: 'BurnCloud Runtime & Change Atlas',
  tagline: 'User Action → Runtime Flow → ICFG → Commit Change Intelligence → Source Evidence',
  url: 'https://burncloud.github.io',
  baseUrl: '/',
  organizationName: 'burncloud',
  projectName: 'burncloud.github.io',
  trailingSlash: true,
  onBrokenLinks: 'throw',
  markdown: {mermaid: true},
  themes: ['@docusaurus/theme-mermaid'],
  presets: [
    ['classic', {
      docs: {
        path: '../content',
        routeBasePath: '/',
        sidebarPath: require.resolve('./sidebars.js'),
        editUrl: 'https://github.com/burncloud/burncloud.github.io/edit/main/content/',
        showLastUpdateAuthor: true,
        showLastUpdateTime: true,
      },
      blog: false,
      theme: {customCss: require.resolve('./src/css/custom.css')},
    }],
  ],
  plugins: [
    ['@docusaurus/plugin-content-docs', {
      id: 'changes',
      path: '../docs',
      routeBasePath: 'changes',
      sidebarPath: require.resolve('./sidebars-changes.js'),
      editUrl: 'https://github.com/burncloud/burncloud.github.io/edit/main/docs/',
      showLastUpdateAuthor: true,
      showLastUpdateTime: true,
    }],
  ],
  themeConfig: {
    navbar: {
      title: 'BurnCloud Atlas',
      items: [
        {type: 'docSidebar', sidebarId: 'runtimeSidebar', position: 'left', label: 'Runtime 执行树'},
        {type: 'docSidebar', sidebarId: 'changesSidebar', docsPluginId: 'changes', position: 'left', label: 'Commit Change Atlas'},
        {href: 'https://github.com/burncloud/burncloud', label: 'BurnCloud Source', position: 'right'},
      ],
    },
    docs: {sidebar: {hideable: true, autoCollapseCategories: false}},
    mermaid: {options: {securityLevel: 'loose'}},
    prism: {theme: lightCodeTheme, darkTheme: darkCodeTheme, additionalLanguages: ['rust', 'bash', 'diff']},
    footer: {style: 'dark', copyright: 'BurnCloud Runtime & Commit Change Atlas · Evidence-first documentation'},
  },
};
