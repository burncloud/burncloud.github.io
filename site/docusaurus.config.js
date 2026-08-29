const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
module.exports = {
  title: 'BurnCloud Documentation',
  tagline: 'Concept → Flow → Interface → Source',
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
      title: 'BurnCloud Docs',
      items: [
        {type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'Technical Reference'},
        {href: 'https://github.com/burncloud/burncloud', label: 'BurnCloud Source', position: 'right'},
      ],
    },
    docs: {sidebar: {hideable: true, autoCollapseCategories: true}},
    mermaid: {options: {securityLevel: 'loose'}},
    prism: {theme: lightCodeTheme, darkTheme: darkCodeTheme, additionalLanguages: ['rust', 'bash', 'sql']},
    footer: {
      style: 'dark',
      copyright: 'BurnCloud Documentation · Concept → Flow → Interface → Source',
    },
  },
};
