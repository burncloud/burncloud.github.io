---
title: "Trust规则"
slug: /architecture/crates/trust/
sidebar_label: "Trust"
---

# Trust 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责 Audit、Evidence、Attestation、Compliance、Risk、Security Governance 等“过程是否真实、合规、可追溯、可证明”的能力。

## 2. 不负责什么

不负责替代 Identity 做身份认证，不负责替代 Traffic 执行请求，不负责替代 Commerce 记账，也不成为全系统日志仓库。

## 3. 可以依赖什么

默认依赖 `kernel`；可以通过其他领域公开事件或公开契约获取需要审计/证明的事实；需要通用基础设施时使用 `platform` 的公开能力。

## 4. 禁止依赖什么

禁止读取其他领域内部表来“顺便审计”；禁止通过 Trust 修改其他领域业务状态；禁止让业务模块反向依赖 Trust 的内部实现。

## 5. 目录和文件

按真实的审计、证据、证明、合规等独立职责向下拆分，不把普通日志、监控和业务历史全部塞进 Trust。

## 6. 代码要求

证据和审计记录必须表达来源、时间、主体和结果；需要不可变性的记录不得通过普通更新接口修改历史事实。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；涉及 Database、Streaming 等能力时按实际引用对应规则。

## 8. 独有测试

重点覆盖审计完整性、Tenant 隔离、证据关联、不可变记录和异常输入。

## 9. 正确示例

```text
Traffic/Commerce 发布公开事实 → Trust 形成审计或证明记录
```

## 10. 错误示例

```text
Trust 直接 UPDATE billing 状态            ❌
Trust 直接查询所有领域私有表作为万能报表    ❌
普通 debug log 全部归入 Trust              ❌
```