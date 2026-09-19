---
title: "interfaces / cli"
slug: /architecture/crates/interfaces/cli/
---

# CLI

继承 [Interfaces规则](./index.md)。

## 独有职责

负责命令、参数、终端输出和退出码。

## 独有要求

- 命令名称表达用户动作。
- 参数解析与业务执行分开。
- 错误使用可判断退出码，不只打印文字后返回成功。
- 默认输出不得泄露密钥。

正确：CLI解析参数后调用公开用例。  
错误：每个CLI命令复制一份数据库和业务逻辑。
