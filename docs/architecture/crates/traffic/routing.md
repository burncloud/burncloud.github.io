---
title: "traffic / routing"
slug: /architecture/crates/traffic/routing/
---

# Routing

继承 [Traffic规则](./index.md)。

## 独有职责

根据请求目标、Supply候选和运行状态形成路由决定。不负责维护Provider目录或执行具体协议请求。

## 独有要求

- 输入候选来自 Supply 公开契约。
- 策略、权重、亲和性和选择结果可解释。
- 没有可用候选时返回明确失败，不伪造默认 Provider。
- 动态选择结果不能写成固定架构事实。

正确：只在合格候选中应用明确策略。  
错误：Routing 自己创建缺失的 Provider 配置。
