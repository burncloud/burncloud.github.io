---
title: "CSS Contract"
slug: /burncloud-ui/architecture/css-contract/
---

# CSS Contract

目标全局样式结构：

```text
assets/styles/
├── reset.css
├── tokens.css
├── typography.css
├── layout.css
├── components.css
└── platform/
```

页面确有专属样式时，可放：

```text
domains/admin/revenue/style.css
```

但必须使用页面 namespace，例如 `.admin-revenue-*`。

业务页面 CSS 禁止定义：

```css
button {}
.card {}
table {}
body {}
```

这类 global selector。

全局视觉规则只能由 Design System / Shared UI ownership 修改。