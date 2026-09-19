---
title: "Download规则"
slug: /architecture/reusable/download/
sidebar_label: "Download规则"
---

# Download 规则

适用于所有下载功能；继承 [基础规则](/architecture/base-rules/)。

- 下载前必须完成资源 Ownership 与权限检查。
- 大文件优先流式传输，避免无必要地整体读入内存。
- 文件名必须经过安全处理，不允许路径穿越或注入非法路径。
- 中断、失败或完成后必须正确释放文件、网络和临时资源。
- 下载逻辑只负责通用传输规则；具体业务对象能否下载，由所属业务规则决定。

例如 Invoice Download 只需补充“只能下载当前 Tenant 拥有的 Invoice”等业务差异，不重复本页规则。