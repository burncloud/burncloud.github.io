---
title: "Directory Contract"
slug: /burncloud-ui/architecture/directory-contract/
---

# Directory Contract

Production Dioxus UI 的目标目录如下。第一阶段保持单一 `crates/client`，先建立模块边界，不提前拆成大量 Cargo crate。

```text
crates/client/src/
├── app/
│   ├── mod.rs
│   ├── app.rs
│   ├── router/
│   │   ├── mod.rs
│   │   ├── routes.rs
│   │   ├── public.rs
│   │   ├── console.rs
│   │   └── not_found.rs
│   └── bootstrap/
│       ├── mod.rs
│       ├── auth.rs
│       ├── i18n.rs
│       └── observability.rs
│
├── auth/
│   ├── mod.rs
│   ├── session.rs
│   ├── auth_gate.rs
│   ├── workspace_gate.rs
│   ├── authorization.rs
│   ├── capabilities.rs
│   └── return_to.rs
│
├── api/
│   ├── mod.rs
│   ├── client.rs
│   ├── error.rs
│   ├── request.rs
│   ├── response.rs
│   ├── buyer/
│   ├── supplier/
│   ├── admin/
│   └── shared/
│
├── domains/
│   ├── buyer/
│   │   ├── mod.rs
│   │   ├── routes.rs
│   │   ├── navigation.rs
│   │   ├── overview/
│   │   ├── marketplace/
│   │   ├── playground/
│   │   ├── api_keys/
│   │   ├── usage/
│   │   ├── billing/
│   │   └── logs/
│   ├── supplier/
│   │   ├── mod.rs
│   │   ├── routes.rs
│   │   ├── navigation.rs
│   │   ├── overview/
│   │   ├── resources/
│   │   ├── deployments/
│   │   ├── reliability/
│   │   ├── earnings/
│   │   ├── settlements/
│   │   └── settings/
│   └── admin/
│       ├── mod.rs
│       ├── routes.rs
│       ├── navigation.rs
│       ├── overview/
│       ├── supply/
│       ├── capacity/
│       ├── demand/
│       ├── models/
│       ├── operations/
│       ├── billing/
│       ├── revenue/
│       ├── settlements/
│       ├── suppliers/
│       ├── customers/
│       ├── settings/
│       └── advanced/
│           ├── providers/
│           ├── routes/
│           ├── logs/
│           ├── guardrails/
│           ├── evaluation/
│           └── team/
│
├── shared/
│   ├── ui/
│   ├── layout/
│   ├── states/
│   ├── hooks/
│   ├── types/
│   ├── validation/
│   └── utils/
│
├── design/
│   ├── tokens.rs
│   ├── typography.rs
│   ├── spacing.rs
│   ├── radius.rs
│   └── breakpoints.rs
│
├── i18n/
│   ├── locale.rs
│   ├── formatter.rs
│   ├── machine_values.rs
│   └── locales/
│       ├── en.rs
│       ├── zh.rs
│       ├── zh_tw.rs
│       └── ja.rs
│
├── platform/
│   ├── web.rs
│   ├── desktop.rs
│   └── liveview.rs
│
├── assets/
│   ├── styles/
│   └── icons/
├── lib.rs
└── main.rs
```

## Page-local Structure

每个业务页面默认采用：

```text
domains/<role>/<page>/
├── mod.rs
├── page.rs
├── model.rs
├── state.rs
├── actions.rs
├── components/
└── tests.rs
```

职责：

- `page.rs`：页面组合，不拥有后端真相。
- `model.rs`：页面 ViewModel / projection，不复制 backend domain model。
- `state.rs`：loading/filter/dialog 等 UI state。
- `actions.rs`：用户动作编排，只调用 typed API。
- `components/`：仅本页面复用的组件。
- `tests.rs`：页面合同与状态测试。

禁止用一个超大 `billing.rs`、`platform.rs`、`analytics.rs` 长期承载多个业务域。