---
title: "commerce / billing / invoice / download"
slug: /architecture/crates/commerce/billing/invoice/download/
---

# Invoice Download

继承 [Invoice规则](./index.md)，并引用 [Download规则](../../../../reusable-rules/download.md)、[Streaming规则](../../../../reusable-rules/streaming.md)和 [HTTP API规则](../../../../reusable-rules/http-api.md)。

## 独有职责

把已经存在的Invoice文档安全提供给有权访问的调用方。

## 独有要求

- 只能下载当前Tenant拥有的Invoice。
- Invoice不存在与无权访问不能泄露额外敏感信息。
- 作废Invoice下载时必须保留作废标记。
- Download不能重新计算或修改Invoice。

正确：通过InvoiceId和Tenant授权后返回文档流。  
错误：接受服务器文件路径，绕过Invoice Owner直接打开文件。
