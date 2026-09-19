---
title: "Crates 目录规则"
slug: /architecture/crates/
---

# Crates 目录规则

`crates/` 第一层只允许八个长期稳定的领域空间：

| 目录 | 唯一问题 |
| --- | --- |
| [kernel](./kernel.md) | 全系统最小、最稳定的基础语义是什么？ |
| [identity](./identity/index.md) | 谁在使用 BurnCloud，有什么身份和权限？ |
| [supply](./supply/index.md) | BurnCloud 有什么模型、Provider 和供应能力？ |
| [traffic](./traffic/index.md) | 请求怎样进入、选择、执行和返回？ |
| [commerce](./commerce/index.md) | 用了多少、多少钱、怎样记账和结算？ |
| [trust](./trust/index.md) | 事情怎样被审计、证明和合规处理？ |
| [platform](./platform/index.md) | 通用技术能力怎样提供？ |
| [interfaces](./interfaces/index.md) | 外部怎样与 BurnCloud 交互？ |

## 每个 crate 的 10 个问题

每一级目录只回答上级尚未回答的部分：

1. Owner 是谁？这个 crate 负责什么？
2. 不负责什么？拥有哪些业务真相和数据？
3. 对外提供哪些公开契约？
4. 可以依赖谁？谁可以依赖它？
5. 禁止哪些依赖、访问和越界行为？
6. 目录和文件怎样组织？
7. 代码应该怎样写？有哪些特殊错误、日志和安全要求？
8. 继承哪些上级规则和可复用规则？
9. 有哪些独有测试、状态、失败和迁移要求？
10. 完整正确示例和完整错误示例是什么？

普通功能必须先归入其中一个一级目录，不能直接增加新的一级 crate。

新增一级领域必须证明：现有八个目录都无法自然容纳，并且它拥有独立业务语言、状态生命周期、Owner 和长期边界。
