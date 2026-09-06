---
title: "Architecture Migration Plan"
slug: /burncloud-ui/architecture/migration-plan/
---

# Architecture Migration Plan

当前 `crates/client` 仍存在 root-level routes、单一 AuthGate、`functional_pages/` 大目录、重复 LiveView route registration 等历史结构。迁移必须小步进行，不能“大重写前端”。

## Recommended Sequence

```text
A. Lock Architecture Contract
↓
B. Establish canonical /console route + Auth/Workspace boundary
↓
C. Establish typed API boundary
↓
D. Establish domains/{buyer,supplier,admin}
↓
E. Move one Golden Page per role
↓
F. Verify dependency/lint rules
↓
G. Migrate remaining pages incrementally
↓
H. Retire functional_pages / legacy roots only after parity
```

## Do Not Big-Bang Rewrite

禁止一次 PR 同时：

```text
重写 Router
重写 Auth
重写全部页面
重写 API client
重写 CSS
重写 Desktop/LiveView
```

每一步都必须保留 current-main Evidence Audit、独立 rollback surface 和明确 human acceptance。

## Cargo Boundary

第一阶段保持一个 `crates/client`。只有当模块确实需要跨产品/平台独立复用或编译边界产生真实价值时，再提取新 crate；目录整洁本身不是拆 crate 的理由。