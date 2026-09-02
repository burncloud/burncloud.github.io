---
title: "BurnCloud 界面实施计划"
slug: /burncloud-ui/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud 界面实施计划

## 第一层：人类阅读区

### TL;DR

这次迁移不是“把 React 翻译成 Dioxus”，而是把批准后的 BurnCloud 产品界面标准落到真实生产客户端。先统一 Design Tokens、Shell 与 Auth/Role，再按 Buyer → Supplier → Admin 迁移页面，并用真实后端数据替换全部 mock。最终同一套 Dioxus UI 同时服务 Web / LiveView / Desktop。

### 为什么要独立实施计划？

当前生产客户端已经有 Dioxus Console，但导航仍以 `Providers / Models / Routes` 等内部对象为主；Target Workbench 已经形成 Buyer / Supplier / Admin 三种不同 Mental Model。若直接逐页复制，会把旧导航、新导航、mock data 和错误权限模型同时留在系统里。

### 目标结构

```text
BurnCloud 界面
├── 实施计划
├── Buyer
│   ├── Overview
│   ├── Playground
│   ├── Marketplace
│   ├── API Keys
│   ├── Usage
│   ├── Billing
│   └── Logs
├── Supplier
│   ├── Overview
│   ├── Resources
│   ├── Deployments
│   ├── Earnings
│   ├── Settlements
│   ├── Reliability
│   └── Settings
└── Admin
    ├── Overview
    ├── Supply
    ├── Capacity
    ├── Demand
    ├── Models
    ├── Revenue
    ├── Settlements
    ├── Suppliers
    ├── Customers
    ├── Operations
    └── Settings
```

### 风险与安全网

> 如果 Target 页面需要生产后端目前不存在的事实，该字段必须显示 `Unknown / Unavailable` 或进入单独 Backend Issue；不能用 mock 把页面“填完整”。

---

## 第二层：机器执行层

### Phase 1 — Foundation

**UI-001：Target Standard → Production Contract**
- 固定 Target truth 与 Current truth 的边界。
- 生产实现只接受批准的 Product / IA / Page Contracts。
- 禁止旧截图、旧通用页面或 Workbench mock 成为业务真相。

**UI-002：Design Tokens + Shared Components**
- 将目标 Typography、Black/White/Gray、状态色、spacing、radius、shadow、control size 映射到 `visual_system.css`。
- 优先复用/补齐 Dioxus 共享组件。
- 字体不得依赖在线 Google Fonts 作为唯一来源。

**UI-003：Production Shell + Role/Auth Workspace**
- 迁移目标 Sidebar、Topbar、Global Search、Workspace Switcher。
- Role 必须来自 Backend Authorization。
- 切换角色后 Sidebar、Overview、搜索范围和权限上下文完整切换。
- 保持 Desktop chrome / system tray / Web / LiveView 兼容。

### Phase 2 — Buyer

顺序：Overview → Marketplace → Playground → API Keys → Usage → Billing → Logs。

```text
Discover Model
→ Test
→ Get Credential
→ Call API
→ Understand Usage
→ Manage Billing
→ Diagnose Request
```

### Phase 3 — Supplier

顺序：Overview → Resources → Deployments → Reliability → Earnings → Settlements → Settings。

硬边界：**资源、部署结果、贡献、收入可见；模型部署和 Traffic 控制不交给 Supplier。**

### Phase 4 — Admin

顺序：Overview → Supply → Capacity → Demand → Models → Operations → Revenue → Settlements → Suppliers → Customers → Settings。

Admin 默认处理系统级结果和异常，不做逐 GPU 日常调度。

### Phase 5 — BurnCloud Node Autopilot UX

统一映射需求驱动 Node 状态：

```text
Provider Serving
Resolving
Preparing
Downloading
Verifying
Starting
Local Ready
Degraded
Unsupported
Failed
Recovered
```

禁止把内部实现变成用户操作：

```text
Download Model
Choose GGUF
Choose GPU Layers
Choose Port
Start llama.cpp
Manage PID
```

### Phase 6 — Compatibility Migration

旧 `/providers`、`/routes`、`/models` 等生产 Route 不得一次性删除：

```text
Current Route
→ identify new owner page
→ compatibility alias / redirect
→ verify automation/tests/deep links
→ separate removal decision
```

### Phase 7 — Gates

- Cargo / Dioxus build
- Web / Desktop / LiveView（适用）
- Auth / role / tenant isolation
- Loading / Empty / Partial Failure / Error / Recovered
- No mock truth
- No duplicate frontend
- Accessibility / keyboard / focus
- Golden Page Visual QA
- Main viewport: 1440×900 + common browser widths
- Final diff no unrelated UI drift

---

## 第三层：Definition of Done

- [ ] Buyer / Supplier / Admin 一级导航符合批准 IA。
- [ ] Role 只来自 Backend Authorization。
- [ ] Workbench mock 已替换为真实 API 或 explicit Unknown。
- [ ] Buyer 不默认看到 GPU / Supplier / IDC / Runtime。
- [ ] Supplier 不拥有手工模型部署、Runtime、Traffic 控制。
- [ ] Admin 默认管理 Supply / Capacity / Demand / Economics。
- [ ] Node 自动准备模型有真实阶段反馈，但没有人工 Start/Download 流程。
- [ ] 旧生产 Route 有兼容与退役策略。
- [ ] Production 仍只有一套 Dioxus frontend。
- [ ] Web / Desktop / LiveView 关键路径通过。
- [ ] Golden Pages 通过 UI Review Checklist。
