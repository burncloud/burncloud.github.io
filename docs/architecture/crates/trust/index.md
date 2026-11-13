---
title: "trust"
slug: /architecture/crates/trust/
---

# `crates/trust`

继承 [基础规则](/architecture/foundation/)。

本页是 Trust 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。

## 负责什么

负责 Audit、Evidence、Attestation、Compliance、Provenance、Risk 和 Security Governance：过程是否真实、合规、可追溯、可证明。

## 不负责什么

不替代 Identity 做身份认证，不执行普通路由，不替代 Traffic 执行请求，不计算客户价格，不替代 Commerce 记账，不管理 Provider 供应目录，也不成为全系统日志仓库。

## 依赖

默认依赖 `kernel`。可以通过其他领域公开事件或公开契约获取需要审计和证明的事实。需要通用基础设施时使用 `platform` 的加密、存储或时间能力。其他领域不能替 Trust 宣布证据有效。

禁止读取其他领域内部表来顺便审计。禁止通过 Trust 修改其他领域业务状态。禁止让业务模块反向依赖 Trust 的内部实现。

## 目录

按真实的审计、证据、证明、合规等独立职责向下拆分。不把普通日志、监控和业务历史全部塞进 Trust。

```text
trust/
├── audit/
├── evidence/
├── attestation/
├── provenance/
└── compliance/
```

## 代码要求

原始事实、验证过程和最终结论分开。证据和审计记录必须表达来源、时间、主体和结果。需要不可变性的记录不得通过普通更新接口修改历史事实。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。涉及 Database、Streaming 等能力时按实际引用对应规则。

## 测试

重点覆盖审计完整性、Tenant 隔离、证据关联、不可变记录、篡改、缺失、签名、权限、可追溯性和异常输入。

## 正确与错误

正确：Traffic 或 Commerce 发布公开事实，Trust 验证后形成审计记录或证明结论。

错误：

```text
Trust 直接 UPDATE billing 状态            ❌
Trust 直接查询所有领域私有表作为万能报表    ❌
普通 debug log 全部归入 Trust              ❌
Traffic 因为请求成功就直接声明“来源已证明”  ❌
```

## 子目录

当前没有已单独成页的 Trust 子规则。下级职责出现独立边界后再增加页面，不在这里预写空页。
