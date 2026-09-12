---
title: "HTTP API规则"
slug: /architecture/reusable/http-api/
sidebar_label: "HTTP API规则"
---

# HTTP API 规则

本页只收录多个实际 HTTP 入口共同需要的规则；继承 [基础规则](/architecture/base-rules/)。

当前不提前规定状态码、DTO、分页或版本策略。等这些规则在真实接口中重复出现后，再从下级页面提取到这里。

所有 HTTP 入口仍必须遵守基础规则中的公开契约、错误处理、日志、安全和测试要求。