---
title: "BurnCloud 界面实施计划"
slug: /burncloud-ui/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud 界面实施计划

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**Canonical Standard：BurnCloud Engineering Issue Standard**

> 本页是 BurnCloud UI 的 canonical 实施计划索引，不是 Codex 的直接开发授权。每一个计划项真正开始实现前，都必须针对当时的 `burncloud/burncloud/main` 重新执行 Evidence Audit，创建通过 READY Gate 的 Engineering Issue，再生成 Task Contract。

### TL;DR

BurnCloud UI 不做“React → Dioxus 翻译”。目标是把批准后的 Buyer / Supplier / Admin 产品合同迁移到唯一的生产 Dioxus Console，并同时锁定 **权限、Console 路径、i18n、真实数据、Node Autopilot 与 legacy compatibility**。

生产 Console 的 canonical namespace 统一为：

```text
PUBLIC
/                     public entry
/login                public auth
/register             public auth

DATA PLANE
/v1/*                  AI API

MANAGEMENT PLANE
/console               authenticated workspace resolver
/console/buyer/*       Buyer workspace
/console/supplier/*    Supplier workspace
/console/admin/*       Admin workspace
/console/api/*         authenticated management API
/console/internal/*    internal API

TRANSPORT / HEALTH
/ws
/health
```

核心原则：

```text
URL namespace
≠ authorization

Sidebar visibility
≠ authorization

Role Switcher
≠ permission grant
```

真正权限始终由 Backend Authorization 决定。

### 执行链

```text
Implementation Plan (PLANNED)
        ↓
Evidence Audit against current main
        ↓
READY Engineering Issue
        ↓
Task Contract
        ↓
Branch / Pull Request
        ↓
Verification / Review
        ↓
main
```

### 计划列表

#### Phase 1 — Foundation / Platform Contracts

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-001](/burncloud-ui/implementation-plan/ui-001/) | Target Standard → Production Contract | 无 |
| [UI-002](/burncloud-ui/implementation-plan/ui-002/) | Design Tokens + Shared Components | 无 |
| [UI-007](/burncloud-ui/implementation-plan/ui-007/) | Production i18n / Localization Contract | UI-001, UI-002 |
| [UI-003](/burncloud-ui/implementation-plan/ui-003/) | Production Shell + Role/Auth Workspace | UI-001, UI-002, UI-007 |
| [UI-008](/burncloud-ui/implementation-plan/ui-008/) | Console Namespace + Route Authorization Contract | UI-003, UI-007 |

#### Phase 2 — Buyer

所有 Buyer 页面都依赖 **UI-003 + UI-007 + UI-008**，并额外依赖自己的 backend contract。

| ID | 页面 | Canonical Production Route | 额外功能依赖 |
| --- | --- | --- | --- |
| [UI-BUYER-001](/burncloud-ui/implementation-plan/ui-buyer-001/) | Overview | `/console/buyer/overview` | Buyer metrics |
| [UI-BUYER-002](/burncloud-ui/implementation-plan/ui-buyer-002/) | Marketplace | `/console/buyer/marketplace` | Product Catalog/Tier/Pricing |
| [UI-BUYER-003](/burncloud-ui/implementation-plan/ui-buyer-003/) | Playground | `/console/buyer/playground` | Marketplace + Node demand states |
| [UI-BUYER-004](/burncloud-ui/implementation-plan/ui-buyer-004/) | API Keys | `/console/buyer/api-keys` | Token ownership contract |
| [UI-BUYER-005](/burncloud-ui/implementation-plan/ui-buyer-005/) | Usage | `/console/buyer/usage` | Usage attribution |
| [UI-BUYER-006](/burncloud-ui/implementation-plan/ui-buyer-006/) | Billing | `/console/buyer/billing` | Buyer financial contracts |
| [UI-BUYER-007](/burncloud-ui/implementation-plan/ui-buyer-007/) | Logs | `/console/buyer/logs` | tenant-safe log projection |

#### Phase 3 — Supplier

所有 Supplier 页面都依赖 **UI-003 + UI-007 + UI-008**。

| ID | 页面 | Canonical Production Route | 额外功能依赖 |
| --- | --- | --- | --- |
| [UI-SUPPLIER-001](/burncloud-ui/implementation-plan/ui-supplier-001/) | Overview | `/console/supplier/overview` | Supplier/Node/Earnings |
| [UI-SUPPLIER-002](/burncloud-ui/implementation-plan/ui-supplier-002/) | Resources | `/console/supplier/resources` | Node inventory/resources |
| [UI-SUPPLIER-003](/burncloud-ui/implementation-plan/ui-supplier-003/) | Deployments | `/console/supplier/deployments` | managed deployments |
| [UI-SUPPLIER-004](/burncloud-ui/implementation-plan/ui-supplier-004/) | Reliability | `/console/supplier/reliability` | reliability evidence |
| [UI-SUPPLIER-005](/burncloud-ui/implementation-plan/ui-supplier-005/) | Earnings | `/console/supplier/earnings` | contribution/earnings |
| [UI-SUPPLIER-006](/burncloud-ui/implementation-plan/ui-supplier-006/) | Settlements | `/console/supplier/settlements` | settlement/payout |
| [UI-SUPPLIER-007](/burncloud-ui/implementation-plan/ui-supplier-007/) | Settings | `/console/supplier/settings` | supplier-owned settings |

Supplier 硬边界：**可以 Observe / Explain / Graceful Offline，但不能获得 Model Deployment、Runtime、Traffic 控制权。**

#### Phase 4 — Admin

所有 Admin 页面都依赖 **UI-003 + UI-007 + UI-008**。

| ID | 页面 | Canonical Production Route | 额外功能依赖 |
| --- | --- | --- | --- |
| [UI-ADMIN-001](/burncloud-ui/implementation-plan/ui-admin-001/) | Overview | `/console/admin/overview` | Revenue/Cost/Capacity |
| [UI-ADMIN-002](/burncloud-ui/implementation-plan/ui-admin-002/) | Supply | `/console/admin/supply` | Supplier/Node/Hardware |
| [UI-ADMIN-003](/burncloud-ui/implementation-plan/ui-admin-003/) | Capacity | `/console/admin/capacity` | Capacity/Demand/Economics |
| [UI-ADMIN-004](/burncloud-ui/implementation-plan/ui-admin-004/) | Demand | `/console/admin/demand` | Demand/Forecast |
| [UI-ADMIN-005](/burncloud-ui/implementation-plan/ui-admin-005/) | Models | `/console/admin/models` | Product Catalog/Manifest |
| [UI-ADMIN-006](/burncloud-ui/implementation-plan/ui-admin-006/) | Operations | `/console/admin/operations` | Autopilot Event/Proposal/Verify |
| [UI-ADMIN-007](/burncloud-ui/implementation-plan/ui-admin-007/) | Revenue | `/console/admin/revenue` | Revenue/Verified Cost |
| [UI-ADMIN-008](/burncloud-ui/implementation-plan/ui-admin-008/) | Settlements | `/console/admin/settlements` | Settlement/Payout + Human Gate |
| [UI-ADMIN-009](/burncloud-ui/implementation-plan/ui-admin-009/) | Suppliers | `/console/admin/suppliers` | Supplier registry/trust/commercial |
| [UI-ADMIN-010](/burncloud-ui/implementation-plan/ui-admin-010/) | Customers | `/console/admin/customers` | Customer Risk/Activity |
| [UI-ADMIN-011](/burncloud-ui/implementation-plan/ui-admin-011/) | Settings | `/console/admin/settings` | domain settings + Human Gate |

#### Phase 5–7 — Cross-cutting / Release

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-004](/burncloud-ui/implementation-plan/ui-004/) | Canonical Node Autopilot UX States | UI-002, UI-003, UI-007, UI-008 + Node state contracts |
| [UI-005](/burncloud-ui/implementation-plan/ui-005/) | Legacy Console Route Compatibility | UI-008 + target page parity |
| [UI-006](/burncloud-ui/implementation-plan/ui-006/) | Final Quality / Golden Page Gates | release pages + UI-004/005/007/008 |

### 全局风险与安全网

- Target truth ≠ current source truth。
- Unknown / Unavailable 不得被 0、Success、Ready 或 mock 替代。
- Production 只有一套 Dioxus frontend / Router。
- `/console/*` 是管理 UI namespace，不是授权事实；Backend Authorization 才是最终权限真相。
- `/console/api/*` 与 `/console/internal/*` 是保留后端 namespace，不能被 LiveView / SPA catch-all 吞掉。
- i18n 不进入 Console URL；语言变化不得改变权限、Route 或 machine identifiers。
- Buyer 不默认看到 GPU / Supplier / IDC / Runtime。
- Supplier 不拥有 Deploy / Runtime / Traffic 权限。
- Admin 管理系统级结果与例外，不退化成逐 PID / GPU 控制台。
- Node 生命周期由后端拥有，UI 只 Observe / Explain / Report。
- Legacy URL 保持原业务语义；不能按当前角色动态改变同一个 bookmark 的产品含义。

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把 BurnCloud UI 拆成 33 个单一结果计划单元，并以 UI-007 与 UI-008 分别作为 localization 和 Console namespace/route 的 canonical contract，使每个页面只有在 current-main 证据、依赖、权限边界和验证目标明确后才可转成 READY Engineering Issue。

### 2. Evidence

Evidence baseline：`burncloud/burncloud@c314bff9646f9113c9a58a818552fc80c77543a6`。

STATIC CONFIRMED：
- 生产客户端是 `crates/client` 下唯一 Dioxus frontend；
- current `app.rs` 受保护页面仍使用根级 `/models`、`/billing` 等 URL，并通过 `AuthGate` 做 authentication；
- current `AuthGate` 只判断 authenticated，不是 Role/Capability Gate；
- Server management API 已 canonical 使用 `/console/api/*`，internal 使用 `/console/internal/*`；
- LiveView 当前仍硬编码旧根级 UI paths；
- Target Workbench 已有 Buyer/Supplier/Admin path 与 `en/zh/zh-TW/ja` i18n reference，但它不是生产权限/路由真相；
- current backend 已有真实 Billing、Usage、Token、Playground、Logs、Customers 等能力片段；
- Supplier、Capacity、Demand Forecast、Settlement、Autopilot Proposal 等目标域仍存在大量 UNKNOWN/backend blockers。

结论：**计划完整 ≠ backend 已存在 ≠ 可以编码。**

### 3. Entry / Starting Point

```text
crates/client/src/app.rs
crates/client/src/auth_gate.rs
crates/client/src/functional_layout.rs
crates/client/src/lib.rs :: liveview_router
crates/client/src/backend.rs
crates/server/src/lib.rs
crates/server/src/api/*
crates/common/src/constants.rs
rustburn/burncloud-ui :: target route/i18n reference
```

### 4. Reuse Targets / Do Not Recreate

Reuse：single Dioxus Router、AuthContext、existing management API namespace、visual_system.css、shared components、real backend services、existing UI gates。

Do Not Recreate：第二套 React frontend、第二 Router、client role DB、client authorization engine、production mock registry、前端 Billing/Settlement/Capacity/Trust truth engine、UI Node Runtime/Process Manager。

### 5. Scope

每个计划页只能授权一个页面或一个横切合同。缺失 backend domain 必须成为依赖/Blocker，不允许为了“让页面完成”扩大 UI Issue scope。

### 6. Behavior Contract

所有页面最少定义 Inputs / Outputs / Ownership / Side Effects；所有状态页必须定义 Loading / Empty / Partial Failure / Error / Recovered。所有 authenticated role pages 必须同时继承：

```text
UI-003 Role/Auth Workspace
UI-007 i18n Contract
UI-008 Console Namespace + Route Authorization Contract
```

### 7. Failure / Forbidden Fallbacks

Forbidden globally：

```text
mock as production truth
URL grants role
localStorage grants role
hidden nav treated as authorization
unknown role -> Admin
unknown metric -> 0/Healthy/Ready
legacy URL changes meaning by active role
language changes path/permission
translated model IDs/API paths/error codes
second frontend/router
UI direct Node runtime control
```

### 8. Impact / Invariants

UI migration may touch frontend navigation/presentation and approved backend projections, but不得改变 data-plane `/v1/*` 语义。保持 single Router、server-side tenant/role authorization、management namespace separation、i18n machine-identifier stability。

### 9. Dependencies

Foundation 顺序：

```text
UI-001 + UI-002
      ↓
UI-007
      ↓
UI-003
      ↓
UI-008
      ↓
Role Pages
      ↓
UI-004 / UI-005
      ↓
UI-006
```

页面自身 backend blocker 仍需单独满足。

### 10. Stop Conditions

```text
STOP IF:
- current main disproves a material route/auth/i18n assumption
- implementing a page requires client-side role/tenant authority
- /console/api or /console/internal can be swallowed by UI catch-all
- legacy route must silently change business meaning
- locale must become part of Console URL to proceed
- machine identifiers must be translated
- a missing backend fact would be filled with mock/client inference
- a second frontend/router/source of truth is required
- meaningful auth/route/i18n/runtime verification cannot be performed
```

---

## 第三层：验收层（Definition of Done）

- [ ] 33 个计划单元均有独立 canonical plan page。
- [ ] `/console` 成为 authenticated Console UI root contract。
- [ ] Buyer/Supplier/Admin canonical paths 全部位于 `/console/{workspace}/*`。
- [ ] `/console/api/*` 与 `/console/internal/*` 保持保留后端 namespace。
- [ ] URL/Sidebar/localStorage 都不能授予角色。
- [ ] 未登录 deep link 有安全 `return_to` 行为；无角色权限返回 explicit forbidden/unavailable。
- [ ] i18n 至少覆盖 `en/zh/zh-TW/ja` contract，且 locale 不进入 Console URL。
- [ ] machine identifiers/model IDs/API paths/error codes 不翻译。
- [ ] Buyer/Supplier/Admin 页面使用真实 API 或 explicit Unknown。
- [ ] Legacy 路由有唯一、语义稳定的 compatibility matrix。
- [ ] Production 仍只有一套 Dioxus frontend / Router。
- [ ] Web / Desktop / LiveView 关键路径可验证。
- [ ] Golden Pages 与 auth/route/i18n matrix 纳入 Final Gate。
