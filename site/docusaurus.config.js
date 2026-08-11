const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
module.exports = {
  title: 'BurnCloud Entry Point Atlas',
  tagline: 'Entry Point → Business Capability → Runtime → State → Source',
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
        path: '../docs',
        routeBasePath: '/',
        sidebarPath: require.resolve('./sidebars.js'),
        editUrl: 'https://github.com/burncloud/burncloud.github.io/edit/main/docs/',
        showLastUpdateAuthor: true,
        showLastUpdateTime: true,
      },
      blog: false,
      theme: {customCss: require.resolve('./src/css/custom.css')},
    }],
  ],
  themeConfig: {
    navbar: {
      title: 'BurnCloud Entry Point Atlas',
      items: [
        {type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'BurnCloud'},
        {href: 'https://github.com/burncloud/burncloud', label: 'BurnCloud Source', position: 'right'},
      ],
    },
    docs: {sidebar: {hideable: true, autoCollapseCategories: false}},
    mermaid: {options: {securityLevel: 'loose'}},
    prism: {theme: lightCodeTheme, darkTheme: darkCodeTheme, additionalLanguages: ['rust', 'bash', 'sql']},
    footer: {
      style: 'dark',
      copyright: 'BurnCloud Entry Point Atlas · Source-derived, entrypoint-first documentation',
    },
  },
};
