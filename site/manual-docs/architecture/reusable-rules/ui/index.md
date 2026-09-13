---
title: "UI 可复用规则"
slug: /architecture/reusable-rules/ui/
---

# UI 可复用规则

本规则适用于所有 UI 实现。BurnCloud Web UI 的目录、路由、认证和 API 边界另见 [`interfaces/web-ui`](../../crates/interfaces/web-ui/index.md)。

## UI 负责什么

UI 负责展示、输入、交互和对服务端事实的投影。UI 不拥有价格、余额、权限、路由结果、运行状态等业务真相。

## 共同规则

- 页面必须明确 Loading、Success、Empty、Error 和 Forbidden 状态。
- Unknown、Pending、Failed 不能显示成成功。
- 页面专属组件留在页面附近；只有真正无业务身份的组件才能进入 `shared/`。
- 请求通过统一的类型化 API 边界，不能在页面和组件中散落传输细节。
- 颜色、间距、字号和圆角来自 Design System，页面不能建立第二套视觉语言。
- 可翻译文字与机器标识必须分开，机器标识不能翻译。

## 子规则

- [状态与业务真相](./state.md)
- [共享组件](./shared-components.md)
- [Design System](./design-system.md)
- [i18n](./i18n.md)
- [CSS](./css.md)
- [UI 测试](./testing.md)

正确：页面调用公开用例，根据明确的返回状态进行展示。  
错误：页面读取数据库、自己计算账单，再把本地结果当成最终事实。
