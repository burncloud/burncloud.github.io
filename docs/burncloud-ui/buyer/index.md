---
title: "Buyer"
slug: /burncloud-ui/buyer/
---

# Buyer

Buyer 的 Mental Model：

```text
Model → API → Usage → Billing
```

Buyer 购买的是 **Model API Capacity**，不是 GPU、Supplier Key、IDC、Worker 或 Deployment。

## 页面

- Overview — 今天用了多少？服务现在稳定吗？
- Playground — 这个模型现在能不能满足需求？
- Marketplace — BurnCloud 有哪些模型可以用？
- API Keys — 如何安全访问 BurnCloud API？
- Usage — API 到底用在了哪里？
- Billing — 余额、充值和账单是什么状态？
- Logs — 某一次请求发生了什么？

## 最高边界

Buyer 默认不需要理解 GPU 型号、Supplier、IDC、CUDA、Runtime、GGUF、PID、内部端口或内部 Route。
