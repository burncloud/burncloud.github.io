---
title: "Architecture Lint"
slug: /burncloud-ui/architecture/architecture-lint/
---

# Architecture Lint

架构规则应尽可能从“人记得”升级为 CI 可验证。

目标 lint：

```text
Buyer MUST NOT import Admin/Supplier private modules
Supplier MUST NOT import Admin/Buyer private modules
shared MUST NOT import domains
Page MUST NOT directly use reqwest/raw HTTP
Page MUST NOT contain raw /console/api/ URL
Page MUST NOT access Database / Service / Provider
Protected production route MUST be under /console/*
/console/api/* and /console/internal/* MUST NOT be UI routes
Machine identifiers MUST NOT be localized
Page CSS MUST NOT create unapproved global selectors
Task Contract MUST declare Allowed/Conditional/Forbidden Paths
```

本 `burncloud.github.io` 仓库首先负责 **documentation governance lint**：确保所有 UI Implementation Issue 自动继承 Architecture Contract。Production source lint 应在 `burncloud/burncloud` 中按独立 Foundation Issue 落地。

禁止为让 CI 通过而关闭 lint 或添加无证据 exemption。