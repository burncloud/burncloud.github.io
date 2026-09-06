---
title: "BurnCloud UI Architecture Contract"
slug: /burncloud-ui/architecture/
hide_table_of_contents: false
---

# BurnCloud UI Architecture Contract

<!-- ARCHITECTURE-CONTRACT: REQUIRED -->

本目录是 **BurnCloud Production UI 的上位架构合同**。它不是建议、示例或设计参考，而是所有 BurnCloud UI 页面实现、UI Engineering Issue、Codex/AI 编程任务和人工 Review 的强制依赖。

> **任何 BurnCloud UI 页面实现都必须先满足 Architecture Contract，再满足页面自己的 Product Contract 与 Implementation Plan。**

## Governance Scope

以下内容自动继承本合同，不需要在每个页面复制同一套规则：

```text
site/manual-docs/burncloud-ui/implementation-plan/ui-*.md
        ↓
READY Engineering Issue
        ↓
Task Contract
        ↓
burncloud/burncloud::crates/client production implementation
```

未来新增的 `UI-*` Implementation Issue 也自动受本合同约束。

## Authority Order

```text
Backend Authorization / Backend Truth
        ↓
BurnCloud UI Architecture Contract
        ↓
Approved Product / Page Contract
        ↓
Implementation Plan
        ↓
READY Engineering Issue
        ↓
Task Contract
        ↓
Code
```

下层不得通过“页面需要”“AI 认为更方便”“当前代码这样写”推翻上层约束。

## Core Invariants

```text
UI-ARCH-001  Protected production UI canonical URL MUST be under /console/*.
UI-ARCH-002  Backend Authorization is final permission authority.
UI-ARCH-003  Page MUST NOT access Database / Service / Provider directly.
UI-ARCH-004  Page MUST NOT scatter raw Management API URLs.
UI-ARCH-005  Buyer / Supplier / Admin business modules are physically separated.
UI-ARCH-006  shared/ may contain only truly cross-domain primitives.
UI-ARCH-007  One Issue may modify only its declared ownership scope.
UI-ARCH-008  Router / Auth / API Core / Design System / Shell are Protected Architecture Zones.
UI-ARCH-009  Server Truth != UI Projection != Ephemeral UI State.
UI-ARCH-010  Route definition has one canonical source of truth.
UI-ARCH-011  Hidden UI != Authorization.
UI-ARCH-012  Unknown / Pending / Failed MUST NOT be rendered as successful truth.
```

## Contract Pages

- [Overview](/burncloud-ui/architecture/overview/)
- [Directory Contract](/burncloud-ui/architecture/directory-contract/)
- [Dependency Rules](/burncloud-ui/architecture/dependency-rules/)
- [Route Contract](/burncloud-ui/architecture/route-contract/)
- [Authorization Contract](/burncloud-ui/architecture/authorization-contract/)
- [API Boundary](/burncloud-ui/architecture/api-boundary/)
- [State Truth Contract](/burncloud-ui/architecture/state-truth-contract/)
- [Shared Component Rules](/burncloud-ui/architecture/shared-component-rules/)
- [Design System](/burncloud-ui/architecture/design-system/)
- [i18n Contract](/burncloud-ui/architecture/i18n-contract/)
- [CSS Contract](/burncloud-ui/architecture/css-contract/)
- [Platform Contract](/burncloud-ui/architecture/platform-contract/)
- [Testing Contract](/burncloud-ui/architecture/testing-contract/)
- [Code Ownership](/burncloud-ui/architecture/code-ownership/)
- [AI Coding Boundaries](/burncloud-ui/architecture/ai-coding-boundaries/)
- [Architecture Lint](/burncloud-ui/architecture/architecture-lint/)
- [Migration Plan](/burncloud-ui/architecture/migration-plan/)

## Definition of Architecture Compliance

一个 UI PR 只有同时满足以下条件，才能称为 Architecture Compliant：

```text
Product behavior correct
AND
Route/Auth boundary correct
AND
Dependency direction correct
AND
Allowed Paths respected
AND
No Protected Zone unauthorized modification
AND
No new source of truth
AND
Machine verification passed
AND
Human review passed
```

`CI green` 本身不等于架构验收。