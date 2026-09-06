---
title: "Architecture Overview"
slug: /burncloud-ui/architecture/overview/
---

# Architecture Overview

BurnCloud UI 的长期目标不是“把页面分文件夹”，而是建立稳定的依赖方向和权限边界，使多人、多个 AI Agent、Web/Desktop/LiveView 能并行演进而不产生第二套 Router、第二套权限或第二套业务真相。

## Target Dependency Direction

```text
app
└── router / bootstrap
      ├── auth
      └── shared layout
             ↓
          domains
   ┌─────────┼─────────┐
   ↓         ↓         ↓
 buyer    supplier    admin
   └─────────┼─────────┘
             ↓
            api
             ↓
      Management API
             ↓
   Backend Authorization
```

底层公共能力：

```text
design
i18n
shared/ui
shared/types
platform
```

## Forbidden Dependency Direction

```text
shared → buyer/admin/supplier          FORBIDDEN
buyer → admin                          FORBIDDEN
supplier → admin                       FORBIDDEN
page → database                        FORBIDDEN
page → backend service crate           FORBIDDEN
page → provider                        FORBIDDEN
page → raw /console/api string         FORBIDDEN
UI state → financial/runtime truth     FORBIDDEN
```

## Two Kinds of Permission

### Runtime Permission

决定用户能看什么、做什么：

```text
Authentication
→ Workspace Authorization
→ Capability
→ Backend Authorization
```

### Code Modification Permission

决定一个 Engineering Issue 能改什么：

```text
L1 Page Domain
L2 Role API / Navigation
L3 Shared / i18n / Design
L4 Router / Auth / API Core / Shell
```

页面 Issue 默认只能拥有 L1；提升到 L2/L3 必须在 Task Contract 明确；L4 必须独立 Architecture/Foundation Issue。