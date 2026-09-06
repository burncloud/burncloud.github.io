---
title: "Design System Contract"
slug: /burncloud-ui/architecture/design-system/
---

# Design System Contract

视觉系统必须由 token 驱动，而不是页面各自定义颜色、阴影、spacing 和 radius。

```text
design/
├── tokens.rs
├── typography.rs
├── spacing.rs
├── radius.rs
└── breakpoints.rs
```

或等价的 `--bc-*` token source of truth。

页面允许组合 token，不允许建立第二套视觉语言。

普通页面 Issue 默认无权修改全局 token。需要新增/改变 token 时必须升级为 L3 Design System 变更，并解释所有受影响页面。