---
title: "Database 规则"
slug: /architecture/reusable-rules/database/
---

# Database 规则

- Database 负责持久化，不替领域决定业务政策。
- 每张业务表只有一个数据 Owner。
- 其他领域不能因为共用数据库就直接读写该表。
- Repository 返回领域需要的数据，不向上层泄露数据库 Row。
- SQL、事务和索引根据真实数据规模设计。
- Schema 变化同时引用 [Migration规则](./migration.md)。

正确：Commerce Repository 保存 Commerce 数据。  
错误：Traffic 直接更新 Commerce 的余额表。
