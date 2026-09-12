const generated = require('./sidebars.js');

const docsSidebar = generated.docsSidebar;
const burncloud = docsSidebar.find(
  (item) => item && item.type === 'category' && item.label === 'BurnCloud',
);

if (!burncloud || !Array.isArray(burncloud.items)) {
  throw new Error('BurnCloud sidebar category not found');
}

const architectureCategory = {
  type: 'category',
  label: '工程架构（必读）',
  collapsed: false,
  link: {type: 'doc', id: 'architecture/index'},
  items: [
    {type: 'doc', id: 'architecture/base-rules', label: '1. 基础规则'},
    {
      type: 'category',
      label: '2. 可复用规则',
      collapsed: false,
      link: {type: 'doc', id: 'architecture/reusable/index'},
      items: [
        {type: 'doc', id: 'architecture/reusable/rust', label: 'Rust通用规则'},
        {type: 'doc', id: 'architecture/reusable/ui', label: 'UI规则'},
        {type: 'doc', id: 'architecture/reusable/database', label: 'Database规则'},
        {type: 'doc', id: 'architecture/reusable/http-api', label: 'HTTP API规则'},
        {type: 'doc', id: 'architecture/reusable/download', label: 'Download规则'},
        {type: 'doc', id: 'architecture/reusable/upload', label: 'Upload规则'},
        {type: 'doc', id: 'architecture/reusable/p2p', label: 'P2P规则'},
        {type: 'doc', id: 'architecture/reusable/streaming', label: 'Streaming规则'},
        {type: 'doc', id: 'architecture/reusable/background-job', label: 'Background Job规则'},
        {type: 'doc', id: 'architecture/reusable/migration', label: 'Migration规则'},
      ],
    },
    {
      type: 'category',
      label: '3. Crates目录规则',
      collapsed: false,
      link: {type: 'doc', id: 'architecture/crates/index'},
      items: [
        {type: 'doc', id: 'architecture/crates/kernel', label: 'Kernel'},
        {type: 'doc', id: 'architecture/crates/identity', label: 'Identity'},
        {type: 'doc', id: 'architecture/crates/supply', label: 'Supply'},
        {type: 'doc', id: 'architecture/crates/traffic', label: 'Traffic'},
        {type: 'doc', id: 'architecture/crates/commerce', label: 'Commerce'},
        {type: 'doc', id: 'architecture/crates/trust', label: 'Trust'},
        {type: 'doc', id: 'architecture/crates/platform', label: 'Platform'},
        {type: 'doc', id: 'architecture/crates/interfaces', label: 'Interfaces'},
      ],
    },
  ],
};

const existingIndex = burncloud.items.findIndex(
  (item) => item && item.type === 'category' && item.label === '工程架构（必读）',
);

if (existingIndex >= 0) {
  burncloud.items[existingIndex] = architectureCategory;
} else {
  burncloud.items.push(architectureCategory);
}

module.exports = {docsSidebar};
