---
title: "Hardware Detection"
slug: /burncloud-node/hardware-detection
---

# Hardware Detection

Hardware Detection 把一台机器转换成 BurnCloud Node 可以理解的统一硬件能力描述，再交给 Model Resolver 判断哪些模型 Variant 可运行。

## 最小硬件画像

| 类别 | 字段示例 |
|---|---|
| OS | Windows / Linux / macOS |
| CPU | 架构、核心数、指令集 |
| Memory | 总 RAM、可用 RAM |
| GPU | Vendor、Model、数量 |
| VRAM | 总显存、可用显存 |
| Driver | 驱动 / Runtime 兼容信息 |
| Disk | 可用空间、模型缓存容量 |

```json
{
  "os": "windows",
  "cpu_arch": "x86_64",
  "ram_mb": 65536,
  "gpu": [{"vendor":"nvidia","model":"RTX 5090","vram_mb":32768}],
  "disk_free_mb": 390000
}
```

## 在请求流程中的位置

```mermaid
flowchart LR
    NAME["Model name"] --> HW["Hardware Detection"]
    HW --> PROFILE["HardwareProfile"]
    PROFILE --> RESOLVER["Model Resolver"]
    RESOLVER --> VARIANT["Compatible variant"]
```

Hardware Detection 只提供真实能力，不直接决定下载哪个模型文件。

## 统一数据源

BurnCloud 应只有一份 `HardwareProfile`，供 Model Resolver、Runtime Manager、UI 和诊断系统共同使用，避免不同模块各自判断硬件。

静态信息可在启动时缓存；可用 RAM、VRAM、磁盘等动态资源在准备模型前重新检查。

## 失败情况

需要明确区分 GPU 驱动不可用、Runtime 不兼容、显存不足、RAM 不足、磁盘不足、设备权限不足等错误。

## 当前源码 / 目标

- **✅ Current**：已有 CPU / memory / disk 等系统监控采集能力。
- **🎯 Node v0.1**：形成面向本地模型决策的统一 `HardwareProfile`，补齐 GPU、VRAM 与 Runtime compatibility。
