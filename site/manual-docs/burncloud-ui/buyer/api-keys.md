---
title: "Buyer API Keys"
slug: /burncloud-ui/buyer/api-keys/
---

# Buyer API Keys

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
API Keys 页面只管理 BurnCloud Credential：Create、Name、Rotate、Revoke，以及适用的 Scope / Spend Limit。完整 Secret 只能在安全创建流程中短暂显示，不能长期明文存在。

### Primary Question
> **我如何安全地访问 BurnCloud API？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Masked key / Status | Supplier Key |
| Created / Last Used | Provider credential |
| Scope / Spend Limit | 长期明文 Secret |
| Rotate / Revoke | 其它租户 Key |

### Reviewer Focus
1. Secret 是否只在允许的创建时刻显示？
2. Rotate/Revoke 是否针对明确对象并有必要确认？
3. Backend Auth 是否始终是最终权限真相？

---

## 第二层：机器执行层

### Production Mapping
- Key list / create / rotate / revoke ← Backend credential API
- Status ← authoritative auth state
- Last used ← auth / usage audit
- Scope / Spend Limit ← Backend policy

### Security Contract
- Secret 不进入 URL、日志或长期 localStorage。
- Buyer 永远拿不到 Supplier / Provider upstream credential。
- 前端 Role / Route 不能绕过 Server authorization。
- 创建成功必须明确说明 Secret 是否仅展示一次。

### State Contract
Empty 要引导创建第一把 Key；Create/Rotate 失败必须明确“未生效”，不能乐观显示成功。

---

## 第三层：Definition of Done
- [ ] Create / Rotate / Revoke 真实工作。
- [ ] Secret 生命周期符合安全合同。
- [ ] 跨租户访问被拒绝。
- [ ] Empty / Error / Recovered 已验证。
- [ ] Workbench 假 Key 已移除。
- [ ] 通过分支 + Pull Request 合并。
