---
title: "Database规则"
slug: /architecture/reusable/database/
sidebar_label: "Database规则"
---

# Database 规则

本页只收录多个实际 crate 共同需要的数据库规则；继承 [基础规则](/architecture/base-rules/)。

当前不预设具体实现规则。数据库相关要求只有在多个真实模块重复出现后，才从下级规则提取到这里。

领域数据 Ownership、禁止跨模块直接读写他人数据等全局要求已经由基础规则定义，不在本页重复。