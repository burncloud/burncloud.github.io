---
title: "架构流程图"
slug: /architecture-flow/
hide_table_of_contents: false
---

# 架构流程图

这套图从外向里看 BurnCloud：先看一次请求怎么走完，再看代码分成哪几个领域、谁用到了谁。给不读代码的人用。方块上是白话；路径和函数在点开的说明里，给要对源码的人。

事实只依据 burncloud/burncloud 的 main 提交 [`879e5276b0ed24c3164ec05750d4f44339e92663`](https://github.com/burncloud/burncloud/commit/879e5276b0ed24c3164ec05750d4f44339e92663)。页面上标成「推断 · 待确认」的内容，是对照代码结构做的推理，不是已经核对过的事实。

## 四层分别看什么

| 层 | 看什么 | 现在 |
| --- | --- | --- |
| L0 | 一次对话请求：调用方 → BurnCloud 网关 → 上游模型，再返回。启动两步单独标成只做一次 | 已完成 |
| L1 | 入口、身份、转发、供给、计费、本地推理、底座，以及谁用到了谁 | 已完成 |
| L2 | 每个领域内部的主要模块，以及一次请求在模块里的走向 | 底座的本机节点已有一页，其余稍后 |
| L3 | 核心路径上的关键步骤和函数 | 稍后 |

L2 先有底座里的本机节点。L3 还没有页面。GPU/Token 交易市场在 L0 里只标成「开发中」，没有画成已经接通的流程。

## 打开图

- [L0 一次请求](pathname:///architecture-flow/l0.html)
- [L1 领域与依赖](pathname:///architecture-flow/l1.html)
- [L2 底座 · 本机节点](pathname:///architecture-flow/node.html)
- [PR 948 变更图（还没合并）](pathname:///architecture-flow/pr-948.html)

两页顶栏可以互相进入，也都能回到这篇说明。点开 L0 的方块，说明里会链到 L1 里对应的领域。

L2 的第一页在底座领域，看本机节点从启动到摘掉。它依据的提交是 [`15ee06fce4c469e510d0c7b335578f4159e846ed`](https://github.com/burncloud/burncloud/commit/15ee06fce4c469e510d0c7b335578f4159e846ed)，和上面 L0、L1 用的提交不是同一个。[PR 948 变更图](pathname:///architecture-flow/pr-948.html)还没合并：新的和改过的部分依据 [`95a7b507d495cf17199efba889c839197c779621`](https://github.com/burncloud/burncloud/commit/95a7b507d495cf17199efba889c839197c779621)，没改的部分仍依据前一个提交。
