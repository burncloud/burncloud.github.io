---
title: "HTTP API 规则"
slug: /architecture/reusable-rules/http-api/
---

# HTTP API 规则

- Handler 负责参数解析、调用公开用例和响应转换。
- Handler 不拥有核心业务规则，也不直接编写跨领域 SQL。
- Request、Response 和内部领域模型分开。
- 错误码保持稳定，不把内部错误和敏感信息原样返回。
- 修改公开接口时必须说明兼容方式和调用方影响。

正确：Handler 把请求转换成 Command，再把结果转换成 Response。  
错误：Handler 同时鉴权、计算价格、操作数据库和选择 Provider。
