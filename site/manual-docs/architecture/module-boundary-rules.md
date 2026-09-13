---
title: "模块边界规则（旧入口）"
slug: /architecture/module-boundary-rules/
unlisted: true
---

# 模块边界规则已合并

原来的单页规则过大，无法针对不同 crate 提供具体要求，现已拆入分层规则体系。

- 所有目录共同底线见[基础规则](./foundation.md)。
- 重复的代码类型要求见[可复用规则](./reusable-rules/index.md)。
- 各 crate 的职责、依赖、代码和测试差异见 [`crates/` 规则](./crates/index.md)。
