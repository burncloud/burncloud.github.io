---
title: "UI CSS"
slug: /architecture/reusable-rules/ui/css/
---

# UI CSS

全局样式只能由 Design System 或 Shared UI Owner 修改。页面专属样式必须放在页面附近，并使用页面 Namespace。

```text
assets/styles/
├── reset.css
├── tokens.css
├── typography.css
├── layout.css
├── components.css
└── platform/
```

正确：`.admin-revenue-chart { ... }`。  
错误：在业务页面中定义 `button { ... }`、`.card { ... }`、`table { ... }` 或 `body { ... }` 等全局选择器。

页面样式必须消费统一 Token，不能复制全局颜色、字号和间距。
