const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
module.exports = {
  title: 'BurnCloud Runtime Flow & ICFG Atlas',
  tagline: 'User Action → End-to-End Flow → ICFG → Source Evidence',
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
  themeConfig: {
    navbar: {
      title: 'BurnCloud Runtime Atlas',
      items: [
        {type: 'docSidebar', sidebarId: 'runtimeSidebar', position: 'left', label: '执行流程'},
        {href: 'https://github.com/burncloud/burncloud', label: 'BurnCloud Source', position: 'right'},
      ],
    },
    docs: {sidebar: {hideable: true, autoCollapseCategories: false}},
    mermaid: {options: {securityLevel: 'loose'}},
    prism: {theme: lightCodeTheme, darkTheme: darkCodeTheme, additionalLanguages: ['rust', 'bash']},
    footer: {style: 'dark', copyright: 'BurnCloud Runtime Flow & ICFG Atlas · Evidence-first documentation'},
  },
};
