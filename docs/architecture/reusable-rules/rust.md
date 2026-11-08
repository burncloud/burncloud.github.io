---
title: "Rust 通用规则"
slug: /architecture/reusable-rules/rust/
---

# Rust 通用规则

- 默认私有，只有稳定边界才使用 `pub`。
- 使用明确类型表达业务含义，避免到处传递无意义的字符串和数字。
- 正常失败使用 `Result`，不能依赖 `unwrap` 处理生产输入。
- 共享依赖版本统一管理，不在子 crate 随意固定另一套版本。
- 没有第二个真实实现时，不提前制造 Trait 和 Factory。
- 代码必须符合 `rustfmt`。
- 命名遵循 Rust 习惯：类型和 trait 用 `UpperCamelCase`，函数、变量、模块用 `snake_case`，常量用 `SCREAMING_SNAKE_CASE`。
- 优先使用最小可见性；能保持私有就不 `pub`，能 `pub(crate)` 就不扩大到公共 API。
- `async` 路径不得直接执行可长期阻塞线程的 I/O 或计算。
- 不用宏、泛型或 trait 层级隐藏本可直接表达的简单逻辑。

具体 crate 如有更严格要求，只补充差异。

正确：

```rust
pub fn parse_tenant_id(value: &str) -> Result<TenantId, TenantIdError> {
    TenantId::try_from(value)
}
```

错误：

```rust
pub fn parse_tenant_id(value: &str) -> String {
    value.parse().unwrap()
}
```
