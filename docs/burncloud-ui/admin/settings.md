---
title: "Admin Settings"
slug: /burncloud-ui/admin/settings/
---

# Admin Settings

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Admin Settings 只管理真正的平台级配置和策略，不成为“所有后端字段的垃圾桶”。普通低风险设置可直接保存；财务、安全、Autopilot 权限和危险策略必须进入明确 High-Risk Gate。

### Primary Question
> **平台级策略和系统设置当前是什么？哪些变更风险高？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Platform Settings | 所有数据库字段 |
| Policy Summary | 无解释 raw env |
| Operational Preferences | Supplier Credential Secret |
| High-risk Gate | 无审计危险开关 |

### Reviewer Focus
1. 每个 setting 是否有明确 Backend Owner？
2. 高风险策略是否显示影响和可回滚性？
3. Settings 是否避免吸收 Models / Capacity / Billing 等其它页面职责？

---

## 第二层：机器执行层
- Settings ← authoritative settings backend
- Domain Policies ← corresponding domain service
- Change Audit ← actor/time/old/new/result

### High-Risk Gate
以下变化默认不能由 UI Agent 或 Autopilot 自行批准：财务规则、安全策略、Autopilot 高风险权限、危险数据操作、不可逆基础设施行为。必须显示原因、影响范围、风险、回滚能力和最终 Verify。

### State Contract
保存失败必须指出哪些字段未生效；Partial Failure 不能把整个设置页恢复成默认值；Unknown 配置不能自动套用前端默认后提交覆盖。

---

## 第三层：Definition of Done
- [ ] 每个设置有 Backend Owner。
- [ ] High-Risk 变更有明确 Gate / Audit / Verify。
- [ ] 页面没有复制其它一级页面职责。
- [ ] Partial Failure 不覆盖真实配置。
- [ ] 通过分支 + Pull Request 合并。
