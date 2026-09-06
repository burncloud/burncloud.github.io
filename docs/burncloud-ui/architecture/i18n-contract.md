---
title: "i18n Contract"
slug: /burncloud-ui/architecture/i18n-contract/
---

# i18n Contract

Supported locales 由 canonical i18n contract 管理。Locale 不进入 Console URL，也不影响 permission。

## Machine Values Never Translate

```text
deepseek-v4
USD
CNY
MODEL_PREPARING
request_id
channel_id
TPM
RPM
TTFT
GPU
VRAM
/v1/chat/completions
```

可翻译的是显示名称、解释、按钮、帮助文字、错误说明。

禁止页面创建自己的 locale dictionary：

```text
domains/buyer/billing/zh.rs  FORBIDDEN
domains/admin/revenue/en.rs   FORBIDDEN
```

统一使用 `i18n/locales/*` 与 centralized formatter。Currency/date/time/percentage/duration/token/bytes 的 formatting 不得页面各写一套。