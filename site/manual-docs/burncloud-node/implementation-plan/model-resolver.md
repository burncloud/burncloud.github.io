---
title: "类别三：Model Resolver"
slug: /burncloud-node/implementation-plan/model-resolver/
---

# 类别三：Model Resolver

Model Resolver 把逻辑 Model ID 转换成当前机器可以执行的具体模型选择，但不下载文件、不启动进程。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-201 | 定义 Model Manifest | 无 | PLANNED |
| NODE-202 | 建立 Canonical Model ID 与 Alias 解析 | NODE-201 | PLANNED |
| NODE-203 | 根据 Hardware / Runtime 选择 Variant | NODE-101~103, NODE-201~202 | PLANNED |
| NODE-204 | 定义 ResolvedModel 与失败诊断合同 | NODE-203 | PLANNED |

Resolver 的输出是稳定合同 `ResolvedModel`，而不是某个临时 GGUF 文件路径。