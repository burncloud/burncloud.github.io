---
title: "Web UI 目录结构"
slug: /architecture/crates/interfaces/web-ui/directory/
---

# Web UI 目录结构

Production Dioxus UI 保持单一客户端 crate，先建立模块边界，不为了目录整洁提前拆成大量 Cargo crate。2026-10-25 的 main `15ee06fce4c469e510d0c7b335578f4159e846ed` 上，这个 crate 是 `crates/interfaces/client`。仓库里已经没有 `crates/client`。

下面的树对应该提交里的 `crates/interfaces/client/src/`。其中 `assets/styles/` 在该提交中不存在；样式文件目前能核对到的是 `src/desktop_chrome.css`。

```text
crates/interfaces/client/src/
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
├── auth/
│   ├── session.rs
│   ├── auth_gate.rs
│   ├── workspace_gate.rs
│   ├── authorization.rs
│   ├── capabilities.rs
│   └── return_to.rs
├── api/
│   ├── client.rs
│   ├── error.rs
│   ├── request.rs
│   ├── response.rs
│   ├── buyer/
│   ├── supplier/
│   ├── admin/
│   └── shared/
├── domains/
│   ├── buyer/
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
├── shared/
│   ├── ui/
│   ├── layout/
│   ├── states/
│   ├── hooks/
│   ├── types/
│   └── validation/
├── design/
│   ├── tokens.rs
│   ├── typography.rs
│   ├── spacing.rs
│   ├── radius.rs
│   └── breakpoints.rs
├── i18n/
│   ├── locale.rs
│   ├── formatter.rs
│   ├── machine_values.rs
│   └── locales/
├── platform/
│   ├── web.rs
│   ├── desktop.rs
│   └── liveview.rs
├── assets/styles/
├── lib.rs
└── main.rs
```

页面内部默认结构：

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

- `page.rs`：组合页面，不拥有后端真相。
- `model.rs`：页面 Projection，不复制后端 Domain Model。
- `state.rs`：Loading、Filter、Dialog、Draft 等 UI 状态。
- `actions.rs`：用户动作编排，只调用 Typed API。
- `components/`：只在本页面复用的组件。
- `tests.rs`：页面合同与状态测试。

禁止长期使用一个超大 `billing.rs`、`platform.rs` 或 `analytics.rs` 承载多个独立职责。
