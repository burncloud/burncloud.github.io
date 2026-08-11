---
title: "start_server"
slug: /startup/start_server
hide_table_of_contents: true
---

# start_server

**树路径：** `BurnCloud → Startup → Startup Chain → start_server`

> **中文解释：** 创建默认数据库 → RouterDatabase::init → UserDatabase::init → create_app → bind → axum::serve。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process startup
│    └─ start_server
│
▼
FILE: crates/server/src/lib.rs
│
├─ 创建默认数据库 → RouterDatabase::init → UserDatabase::init → create_app → bind → axum::serve。
├─ DECISION: initialization step fails?
│    ├─ YES → propagate error / process startup fails
│    └─ NO  → continue next initialization stage
│
├─ Runtime objects / routes / tasks become available
│
▼
END
     └─ server/client/runtime enters steady state
```


## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
database=connected
router_db=initialized
user_db=initialized
listener=0.0.0.0:3000
server=running
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
