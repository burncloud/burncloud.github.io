---
title: "UI Design System"
slug: /architecture/reusable-rules/ui/design-system/
---

# UI Design System

颜色、字体、间距、圆角和断点必须来自一个稳定的 Token 来源，例如：

```text
design/
├── tokens.rs
├── typography.rs
├── spacing.rs
├── radius.rs
└── breakpoints.rs
```

页面可以组合 Token，不能直接建立新的全局视觉规则。普通页面 Issue 默认不能修改全局 Token；确需修改时，应声明为 Conditional Path 并说明受影响页面。

正确：页面使用 `spacing::MD` 和语义颜色。  
错误：每个页面各自写一套颜色、阴影和间距常量。
