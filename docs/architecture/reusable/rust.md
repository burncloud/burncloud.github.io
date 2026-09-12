---
title: "Rust通用规则"
slug: /architecture/reusable/rust/
sidebar_label: "Rust通用规则"
---

# Rust 通用规则

适用于引用本规则的 Rust crate；继承 [基础规则](/architecture/base-rules/)。

- 代码必须符合 `rustfmt`。
- 命名遵循 Rust 习惯：类型/trait 用 `UpperCamelCase`，函数、变量、模块用 `snake_case`，常量用 `SCREAMING_SNAKE_CASE`。
- 优先使用最小可见性；能 `private` 就不 `pub`，能 `pub(crate)` 就不扩大到公共 API。
- `async` 路径不得直接执行可长期阻塞线程的 I/O 或计算。
- 不用宏、泛型或 trait 层级隐藏本可直接表达的简单逻辑。

具体 crate 如有更严格要求，只补充差异。