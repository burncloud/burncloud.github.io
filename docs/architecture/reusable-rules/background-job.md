---
title: "Background Job 规则"
slug: /architecture/reusable-rules/background-job/
---

# Background Job 规则

- 每个任务有明确输入、Owner、状态和结束条件。
- 后台任务不能悄悄改变另一个领域的业务数据。
- 是否允许重试、最多几次和重复执行的结果由任务自己定义。
- 服务重启后是否继续，必须明确说明。
- 失败必须可见，不能无限循环或吞掉错误。

正确：任务记录失败并按自己的规则有限重试。  
错误：永久循环，任何错误都立即重试且没有停止条件。
