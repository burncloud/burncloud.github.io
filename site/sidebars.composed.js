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
    {type: 'doc', id: 'architecture/directory-rules', label: '目录规则'},
  ],
};

if (!burncloud.items.some(
  (item) => item && item.type === 'category' && item.label === '工程架构（必读）',
)) {
  burncloud.items.push(architectureCategory);
}

module.exports = {docsSidebar};
