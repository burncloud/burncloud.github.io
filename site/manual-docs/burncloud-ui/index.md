---
title: "BurnCloud 界面"
slug: /burncloud-ui/
hide_table_of_contents: false
---

# BurnCloud 界面

BurnCloud 界面是 BurnCloud 产品层的目标 UI / UX 文档域。

> **`rustburn/burncloud-ui` 定义目标产品、Page Contracts 与 Golden Pages；`burncloud/burncloud/crates/client` 是生产 Dioxus 实现。**

迁移的是产品合同、信息架构、设计语言、页面状态和交互语义，不是把 React/Vite/Tailwind 代码复制进 BurnCloud。

## 四个一级节点

1. **实施计划** — Workbench → Production Dioxus 的迁移顺序、边界与 Gate。
2. **Buyer** — `Model → API → Usage → Billing`。
3. **Supplier** — `GPU → Health → Contribution → Earnings`。
4. **Admin** — `Supply → Capacity → Demand → Economics`。

## Truth Model

```text
Target Product / UI
rustburn/burncloud-ui
├── workbench_docs/product-standard.md
├── workbench_docs/information-architecture.md
├── workbench_docs/page-contracts/*
├── workbench_docs/design-system.md
├── workbench_docs/interaction-rules.md
└── Golden Pages
        ↓
Production Implementation
burncloud/burncloud
└── crates/client (Dioxus)
```

- **Target truth**：批准后的 BurnCloud UI Standard / Page Contract。
- **Current truth**：当前 `burncloud/burncloud` 源码、API、测试与运行证据。
- Target 文档存在不代表生产功能已经完成。

## 迁移硬规则

- 不引入 React 作为第二套 Production Frontend。
- 不机械复制旧 `src/pages/*`；以当前 Role Routes + Page Contracts 为准。
- Role Switcher 只能切换后端已授权角色，不能成为权限来源。
- Mock data 不进入生产；Unknown 不能伪装成成功。
- Supplier 不获得模型部署、Runtime 或 Traffic 的手工控制权。
- BurnCloud Node 的下载、启动、停止、恢复遵循 Autopilot；UI 负责 Observe / Explain / Report。
- 视觉语义统一映射到 `--bc-*` tokens。
- 所有重要页面覆盖完整状态，不只做 happy path。
