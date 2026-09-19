---
title: "可复用规则"
slug: /architecture/reusable-rules/
---

# 可复用规则

可复用规则解决“不同领域里反复出现的同一种代码应该怎样写”。

| 规则 | 适用对象 |
| --- | --- |
| [Rust 通用规则](./rust.md) | 所有 Rust 代码 |
| [UI 规则](./ui/index.md) | 页面、组件、状态与交互 |
| [Database 规则](./database.md) | Repository、SQL、数据访问 |
| [HTTP API 规则](./http-api.md) | Handler、DTO、HTTP 响应 |
| [Download 规则](./download.md) | 文件下载能力 |
| [Upload 规则](./upload.md) | 文件上传能力 |
| [P2P 规则](./p2p.md) | 节点、连接与消息 |
| [Streaming 规则](./streaming.md) | 流式输入与输出 |
| [Background Job 规则](./background-job.md) | 后台任务 |
| [Migration 规则](./migration.md) | 数据结构迁移 |

一个目录可以引用多份可复用规则。例如 `Invoice Download` 同时引用 HTTP API、Download、Streaming 和安全相关基础规则。

可复用规则不能拥有 Billing、User、Provider 等具体业务事实。
