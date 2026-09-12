---
title: "可复用规则"
slug: /architecture/reusable/
sidebar_label: "2. 可复用规则"
description: "跨多个 crate 复用、但不适合放入全局基础规则的规则。"
---

# 可复用规则

可复用规则解决“多个不同 crate 反复出现同一种能力”时的重复问题。

原则只有两条：

1. 下级规则通过引用使用，不复制正文；
2. 同一规则在两三个真实位置重复后再提取，不提前制造抽象。

当前预留的复用主题：

- Rust 通用规则
- UI 规则
- Database 规则
- HTTP API 规则
- Download 规则
- Upload 规则
- P2P 规则
- Streaming 规则
- Background Job 规则
- Migration 规则

这些页面不是要求所有 crate 使用。只有实际功能匹配时才引用，并允许具体 crate 在其上补充更严格的差异规则。