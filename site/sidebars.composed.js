const sidebars = require('./sidebars.js');

const doc = (id, label) => ({type: 'doc', id, label});

const architecture = {
  type: 'category',
  label: '代码规则（必读）',
  link: {type: 'doc', id: 'architecture/index'},
  items: [
    doc('architecture/foundation', '基础规则'),
    {
      type: 'category',
      label: '可复用规则',
      link: {type: 'doc', id: 'architecture/reusable-rules/index'},
      items: [
        doc('architecture/reusable-rules/rust', 'Rust 通用规则'),
        {
          type: 'category',
          label: 'UI 规则',
          link: {type: 'doc', id: 'architecture/reusable-rules/ui/index'},
          items: [
            doc('architecture/reusable-rules/ui/state', '状态与业务真相'),
            doc('architecture/reusable-rules/ui/shared-components', '共享组件'),
            doc('architecture/reusable-rules/ui/design-system', 'Design System'),
            doc('architecture/reusable-rules/ui/i18n', 'i18n'),
            doc('architecture/reusable-rules/ui/css', 'CSS'),
            doc('architecture/reusable-rules/ui/testing', 'UI 测试'),
          ],
        },
        doc('architecture/reusable-rules/database', 'Database 规则'),
        doc('architecture/reusable-rules/http-api', 'HTTP API 规则'),
        doc('architecture/reusable-rules/download', 'Download 规则'),
        doc('architecture/reusable-rules/upload', 'Upload 规则'),
        doc('architecture/reusable-rules/p2p', 'P2P 规则'),
        doc('architecture/reusable-rules/streaming', 'Streaming 规则'),
        doc('architecture/reusable-rules/background-job', 'Background Job 规则'),
        doc('architecture/reusable-rules/migration', 'Migration 规则'),
      ],
    },
    {
      type: 'category',
      label: 'Crates 目录规则',
      link: {type: 'doc', id: 'architecture/crates/index'},
      items: [
        doc('architecture/crates/kernel', 'Kernel'),
        doc('architecture/crates/identity/index', 'Identity'),
        doc('architecture/crates/supply/index', 'Supply'),
        {
          type: 'category',
          label: 'Traffic',
          link: {type: 'doc', id: 'architecture/crates/traffic/index'},
          items: [
            doc('architecture/crates/traffic/gateway', 'Gateway'),
            doc('architecture/crates/traffic/routing', 'Routing'),
            doc('architecture/crates/traffic/execution', 'Execution'),
            doc('architecture/crates/traffic/rate-limit', 'Rate Limit'),
            doc('architecture/crates/traffic/failover', 'Failover'),
          ],
        },
        {
          type: 'category',
          label: 'Commerce',
          link: {type: 'doc', id: 'architecture/crates/commerce/index'},
          items: [
            doc('architecture/crates/commerce/metering', 'Metering'),
            doc('architecture/crates/commerce/pricing', 'Pricing'),
            doc('architecture/crates/commerce/balance', 'Balance'),
            {
              type: 'category',
              label: 'Billing',
              link: {
                type: 'doc',
                id: 'architecture/crates/commerce/billing/index',
              },
              items: [
                {
                  type: 'category',
                  label: 'Invoice',
                  link: {
                    type: 'doc',
                    id: 'architecture/crates/commerce/billing/invoice/index',
                  },
                  items: [
                    doc(
                      'architecture/crates/commerce/billing/invoice/download',
                      'Invoice Download',
                    ),
                  ],
                },
              ],
            },
            doc('architecture/crates/commerce/settlement', 'Settlement'),
          ],
        },
        doc('architecture/crates/trust/index', 'Trust'),
        {
          type: 'category',
          label: 'Platform',
          link: {type: 'doc', id: 'architecture/crates/platform/index'},
          items: [
            doc('architecture/crates/platform/cache', 'Cache'),
            doc('architecture/crates/platform/configuration', 'Configuration'),
          ],
        },
        {
          type: 'category',
          label: 'Interfaces',
          link: {type: 'doc', id: 'architecture/crates/interfaces/index'},
          items: [
            doc('architecture/crates/interfaces/http', 'HTTP'),
            {
              type: 'category',
              label: 'Web UI',
              link: {type: 'doc', id: 'architecture/crates/interfaces/web-ui/index'},
              items: [
                doc('architecture/crates/interfaces/web-ui/directory', '目录结构'),
                doc('architecture/crates/interfaces/web-ui/dependencies', '依赖规则'),
                doc('architecture/crates/interfaces/web-ui/route', 'Route'),
                doc('architecture/crates/interfaces/web-ui/authorization', 'Authorization'),
                doc('architecture/crates/interfaces/web-ui/api-boundary', 'API Boundary'),
                doc('architecture/crates/interfaces/web-ui/platform', '多平台边界'),
                doc('architecture/crates/interfaces/web-ui/change-scope', '修改范围'),
                doc('architecture/crates/interfaces/web-ui/migration', '迁移规则'),
              ],
            },
            doc('architecture/crates/interfaces/cli', 'CLI'),
            doc('architecture/crates/interfaces/websocket', 'WebSocket'),
          ],
        },
      ],
    },
  ],
};

const burnCloud = sidebars.docsSidebar.find(
  (item) => item.type === 'category' && item.label === 'BurnCloud',
);

const burnCloudUi = burnCloud?.items.find(
  (item) => item.type === 'category' && item.label === 'BurnCloud 界面',
);

const legacyUiArchitectureIndex = burnCloudUi?.items.findIndex(
  (item) => item.type === 'category' && item.label === '架构规范（必读）',
);

if (legacyUiArchitectureIndex >= 0) {
  burnCloudUi.items.splice(
    legacyUiArchitectureIndex,
    1,
    doc('burncloud-ui/architecture/index', '架构规则（已迁移）'),
  );
}

if (burnCloud && !burnCloud.items.some(
  (item) => item.type === 'category' && item.label === architecture.label,
)) {
  burnCloud.items.push(architecture);
}

module.exports = sidebars;
