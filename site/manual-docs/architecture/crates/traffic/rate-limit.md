---
title: "traffic / rate-limit"
slug: /architecture/crates/traffic/rate-limit/
---

# Rate Limit

继承 [Traffic规则](./index.md)。

## 独有职责

根据已经确定的限流政策控制请求进入速度。不负责价格、余额和长期配额结算。

## 独有要求

- 限流Key、窗口、单位和作用范围必须明确。
- 拒绝结果与Provider失败分开。
- 并发下不能因为竞争让限制失效。
- 规则更新不能无意清除所有租户状态。

正确：按Tenant和Credential的明确维度限流。  
错误：把客户余额不足当成普通速率限制。
