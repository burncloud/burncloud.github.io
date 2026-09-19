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
