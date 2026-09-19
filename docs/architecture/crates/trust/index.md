---
title: "trust"
slug: /architecture/crates/trust/
---

# `crates/trust`

## 负责什么

负责 Audit、Evidence、Attestation、Compliance、Provenance 和风险证明。

## 不负责什么

不执行普通路由、不计算客户价格、不管理 Provider 供应目录。

## 依赖

接收其他领域发布的事实和证据，通过 Platform 的加密、存储或时间能力完成验证。其他领域不能替 Trust 宣布证据有效。

## 目录

```text
trust/
├── audit/
├── evidence/
├── attestation/
├── provenance/
└── compliance/
```

## 代码与测试

原始事实、验证过程和最终结论分开；测试聚焦篡改、缺失、签名、权限和可追溯性。

## 正确与错误

正确：Traffic 提交执行证据，Trust 验证后生成结论。  
错误：Traffic 因为请求成功就直接声明“来源已证明”。
