---
title: "Route Contract"
slug: /burncloud-ui/architecture/route-contract/
---

# Route Contract

## Canonical Namespace

```text
PUBLIC
/
/login
/register

DATA PLANE
/v1/*

MANAGEMENT UI
/console/buyer/*
/console/supplier/*
/console/admin/*

MANAGEMENT API
/console/api/*
/console/internal/*

TRANSPORT
/ws

HEALTH
/health
```

任何需要 authentication、role、tenant、capability 或 admin authority 的 production UI canonical URL 必须位于 `/console/*`。

## One Route Source of Truth

Production Route Definition 必须只有一个 canonical source，例如：

```text
app/router/routes.rs
```

Web、Desktop、LiveView 只能消费同一份 route contract，不允许 `app.rs` 与 `liveview_router()` 各自维护第二份页面列表。

## Reserved Namespace

`/console/api/*` 与 `/console/internal/*` 永远属于 backend。UI catch-all 不得吞掉它们。

## Legacy

Retired root UI URL 不得继续作为 page/alias/redirect；如果保留 temporary compatibility，必须是无业务逻辑 redirect-only，并由 UI-005/UI-008 的明确合同授权。