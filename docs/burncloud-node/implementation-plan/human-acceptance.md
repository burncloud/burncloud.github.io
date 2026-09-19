---
title: "Node 人类验收标准"
slug: /burncloud-node/implementation-plan/human-acceptance/
---

# BurnCloud Node 人类验收标准

本页是 BurnCloud Node Implementation Plan 的 **Human Acceptance Registry**。

机器测试、CI、静态分析、Agent Review 都不能替代这里的人类验收。每个 NODE Issue 在进入 DONE 前，必须由产品负责人、架构负责人或指定工程师按照对应步骤亲自验证，并留下可复查的人工证据。

## 人类验收总原则

```text
AI says done        != Human accepted
CI green            != Product accepted
Unit tests pass     != Human accepted
Screenshot looks OK != Human accepted
```

人工验收至少回答四个问题：

1. **人实际做什么？** — 使用真实 CLI、HTTP 请求、节点环境、文件或运行状态完成操作。
2. **人应该看到什么？** — 明确可观察结果，不依赖阅读内部实现猜测。
3. **什么情况必须判失败？** — 明确禁止“看起来差不多”的结果。
4. **留下什么证据？** — 命令输出、请求/响应、状态截图、日志片段或可复现步骤。

人工验收默认使用接近生产的运行路径；如果只能使用 fixture / mock，必须在验收记录里说明为什么该 mock 不会改变被验收的产品行为。

---

## NODE-001 — Node Core 启动入口与生命周期

**验收者：** 产品负责人 + Runtime 工程师。

**人工步骤：**
1. 在可执行环境中直接运行 `burncloud node`。
2. 确认它进入独立 Node runtime，而不是打印后偷偷转成 `burncloud server` / `burncloud router`。
3. 发出正常停止信号（例如 Ctrl+C / SIGTERM）。
4. 再分别启动现有 `burncloud server`、`burncloud router`，确认原行为没有被改坏。

**人类通过标准：** Node 能明确启动、运行、停止；停止后没有由 Node Core 自己遗留的生命周期任务；现有 server/router 仍可正常启动。

**人工判定失败：** Node 启动即静默 fallback 到其它模式、停止无响应、退出后仍残留 Node 自己创建的长期任务，或现有 server/router 行为变化。

**建议证据：** 启动输出 + 停止输出 + 三种 runtime 的人工运行记录。

## NODE-002 — Node 配置与共享上下文

**验收者：** 架构负责人 + Runtime 工程师。

**人工步骤：**
1. 用一份最小合法 Node 配置启动 Node。
2. 故意缺失一个必需配置，确认启动失败原因清晰。
3. 查看运行诊断或调试输出，确认核心依赖来自同一个 NodeContext / composition root，而不是多个模块各自重新创建 Database / Router / Settings。
4. 修改一个 Node 配置值并重启，确认所有依赖该值的模块看到一致结果。

**人类通过标准：** 配置来源唯一、错误可解释、共享依赖只初始化一次，Context 不表现为业务逻辑容器。

**人工判定失败：** 不同模块读到不同配置、缺失配置被隐藏默认值掩盖、出现第二份 Database/Router/Settings，或 Context 开始承担下载/路由/进程业务。

**建议证据：** 正常启动记录 + 缺失配置错误 + 初始化日志/诊断。

## NODE-003 — 组合现有 Server / Router 为 Node 模式

**验收者：** 产品负责人 + API/Router 工程师。

**人工步骤：**
1. 启动 `burncloud node`。
2. 使用正常 BurnCloud credential 请求 `http://localhost:3000/v1/...`。
3. 确认请求仍经过现有统一 Server / ModelRouter，而不是新的 NodeGateway/LocalRouter。
4. 同时验证一个现有 Provider-only 请求仍可正常完成。

**人类通过标准：** Node 只有一个外部 AI API 入口；Provider routing、Auth、Billing/Quota 的现有产品行为保持不变。

**人工判定失败：** 出现第二端口/第二 Gateway、Local 绕过 ModelRouter、Provider-only 请求行为变化，或 Node 模式放松 Auth/Billing。

**建议证据：** `/v1` 请求/响应 + Provider 请求记录 + 实际监听端口/启动日志。

## NODE-004 — Gateway / Protocol Routing Compatibility Gate

**验收者：** API 负责人 + 产品负责人。

**人工步骤：**
1. 分别发送 OpenAI Chat、OpenAI Responses、Anthropic Messages、Gemini、Ollama 代表性请求。
2. 在同协议上游场景加入 BurnCloud 不认识的 vendor 字段、query、header 和 streaming，确认仍被保留。
3. 选择一个确实需要跨协议转换的场景，确认只有该场景进入 Translator。
4. 请求一个不支持的协议/无效路径，确认得到明确错误而不是错误路由到其它 Provider。

**人类通过标准：** URL 识别协议、model_id 参与路由、同协议 Raw Proxy、不同协议 Translator；未知字段和流式语义在同协议路径不被 BurnCloud 重建丢失。

**人工判定失败：** 所有请求都先转成统一 Body、未知字段消失、streaming 被破坏、URL 直接绑定 Provider、或协议错误被静默兜底。

**建议证据：** 至少五种协议的真实请求/响应样例 + 一个 Raw Proxy 字段保留对比 + 一个 Translator 对比。

## NODE-101 — Canonical HardwareProfile

**验收者：** Runtime 工程师。

**人工步骤：**
1. 在一台已知硬件配置的机器上启动 HardwareProfile 采集。
2. 手工用系统命令核对 OS、CPU、RAM、Disk 等关键字段。
3. 重复读取 HardwareProfile，确认不同 Node 模块看到的是同一份权威事实来源。

**人类通过标准：** 静态硬件字段与机器真实信息一致；不存在 Resolver、Runtime、UI 各自形成不同硬件画像。

**人工判定失败：** 关键字段与系统事实不一致、同一进程出现两份互相冲突的 HardwareProfile，或未知值被伪造成 0/可用。

**建议证据：** HardwareProfile 输出 + 系统命令对照。

## NODE-102 — NVIDIA GPU / VRAM / Driver Detection

**验收者：** GPU/Runtime 工程师。

**人工步骤：**
1. 在 NVIDIA 机器上将 BurnCloud 检测结果与 `nvidia-smi` 或等价可信工具逐项对比 GPU 型号、数量、VRAM、Driver。
2. 在驱动异常/不可访问环境中重复检测。
3. 如果有多卡机器，确认每张卡不会被合并成虚假单卡事实。

**人类通过标准：** NVIDIA 事实准确；驱动不可用时明确报不可用/未知，而不是假装没有 GPU 或填 0。

**人工判定失败：** GPU 数量/显存错误、驱动错误被隐藏、不可访问 GPU 被当作可运行。

**建议证据：** BurnCloud 输出与 `nvidia-smi` 对照截图/文本。

## NODE-103 — Runtime Compatibility 与资源快照

**验收者：** Runtime 工程师。

**人工步骤：**
1. 在同一台机器上先采集资源快照，再人为制造 RAM/VRAM/Disk 压力后重新采集。
2. 确认动态可用资源会变化，而静态硬件身份保持稳定。
3. 用一个明确支持和一个明确不支持的 Runtime 条件验证 compatibility 结果。

**人类通过标准：** 资源快照反映当前现实；Runtime compatibility 有真实原因，不使用旧缓存假装可用。

**人工判定失败：** 动态资源永远不变、资源不足仍显示 compatible、或不同模块自行重新解释硬件事实。

**建议证据：** 压力前后快照 + compatibility 诊断。

## NODE-201 — Model Manifest + Curated Catalog

**验收者：** 模型产品负责人 + Runtime 工程师。

**人工步骤：**
1. 打开 v0.1 curated catalog，随机选择多个模型核对 canonical model、variant、runtime、artifact、资源要求、完整性字段。
2. 故意引用一个 catalog 不存在的 model。
3. 检查 Manifest 中是否存在需要运行时猜测的关键事实。

**人类通过标准：** catalog 是显式、可审阅、有限集合；关键 Artifact/Runtime/资源事实可以由人核实；未知模型明确不存在。

**人工判定失败：** 运行时通过文件名/网络搜索猜 Manifest、关键字段缺失却默认成功，或 catalog 与实际 Artifact 不一致。

**建议证据：** curated catalog 条目抽检记录。

## NODE-202 — Canonical Model ID / Alias

**验收者：** 模型产品负责人。

**人工步骤：**
1. 对同一模型分别使用 canonical ID 和批准的 alias 发起解析。
2. 确认它们归一到同一个 canonical identity。
3. 输入近似拼写、未批准 alias 和冲突 alias。

**人类通过标准：** 只有明确声明的 alias 才归一；不会因模糊匹配把用户请求变成另一个模型。

**人工判定失败：** typo 被“智能猜测”为其它模型、两个 canonical model 共享冲突 alias、或 alias 结果随运行环境变化。

**建议证据：** canonical/alias 输入输出表。

## NODE-203 — Hardware/Runtime 驱动的 Variant 选择

**验收者：** 模型负责人 + GPU/Runtime 工程师。

**人工步骤：**
1. 在至少两种资源档位上解析同一个逻辑模型。
2. 确认选择的 Variant 与 HardwareProfile/Runtime 能力相符。
3. 制造显存不足或 Runtime 不支持，确认返回结构化 reject reason。

**人类通过标准：** 用户只选择模型，不选择 GGUF；可运行时选出可解释 Variant，不可运行时解释真实原因。

**人工判定失败：** 任意挑最小 GGUF 兜底、资源不足仍输出可运行 Variant，或 Resolver 自己触发下载/启动。

**建议证据：** 不同机器/资源档位的解析对比。

## NODE-204 — ResolvedModel / ResolutionFailure 合同

**验收者：** 架构负责人 + Runtime 工程师。

**人工步骤：**
1. 对一个可解析模型查看完整 ResolvedModel。
2. 对多个失败场景查看 ResolutionFailure。
3. 让后续 Preparation/Runtime 人工消费这些结果，确认无需重新猜 model/variant/runtime 事实。

**人类通过标准：** 成功和失败都是稳定、结构化、可被下游直接理解的合同。

**人工判定失败：** 下游必须重新解析文件名、重新检测硬件或解析自由文本才能继续。

**建议证据：** 一份成功合同 + 至少两份失败合同。

## NODE-301 — Local Artifact State

**验收者：** 模型/Runtime 工程师。

**人工步骤：**
1. 分别准备“不存在、下载中、已验证、失败/损坏”的 Artifact。
2. 查看 Node 报告的 ABSENT/PREPARING/READY/FAILED 或等价状态。
3. 重启 Node 后再次检查状态。

**人类通过标准：** 文件存在不等于 READY；重启后可安全恢复或重新判定；状态与 Process READY 完全分离。

**人工判定失败：** `.gguf` 文件一出现就 READY、stale 状态重启后继续伪装 READY、或 Artifact failure 直接污染 Runtime state。

**建议证据：** 四种状态的人工检查记录 + 重启前后对比。

## NODE-302 — 后台 Prepare / 磁盘准入 / 下载去重

**验收者：** 产品负责人 + 下载/Runtime 工程师。

**人工步骤：**
1. 对同一未安装模型同时发起多次真实 model demand。
2. 观察下载任务列表/日志，确认只有一个 active download/prepare。
3. 在磁盘不足环境再次触发，确认下载在开始前被拒绝。
4. 中断一次下载并恢复，确认复用现有可恢复任务。

**人类通过标准：** 请求线程不等待大型下载；同 Artifact 只准备一次；磁盘不足不先下载再失败；可恢复下载不重新从零制造第二任务。

**人工判定失败：** N 个请求产生 N 个下载、磁盘不足仍开下、Provider 响应等待本地下载、或新建第二套 downloader。

**建议证据：** 并发请求记录 + 下载任务数 + 磁盘不足错误。

## NODE-303 — Artifact 校验 / 失败 / 恢复

**验收者：** 模型/Runtime 工程师。

**人工步骤：**
1. 准备一个正确 Artifact、一个截断文件、一个 checksum 错误文件。
2. 分别执行验证。
3. 修复损坏文件后重新验证。

**人类通过标准：** 只有满足 Manifest 要求的 Artifact 才 READY；损坏/部分文件有明确原因；修复后必须重新验证才能 READY。

**人工判定失败：** checksum mismatch 只 warning 后继续、下载 complete 自动等于 READY、或通过“启动 llama-server 看看”替代 Artifact 校验。

**建议证据：** valid/mismatch/partial/recovery 四组结果。

## NODE-304 — Artifact Inventory / Cache / Delete Lifecycle

**验收者：** 产品负责人 + 模型存储工程师。

**人工步骤：**
1. 准备至少两个本地 Artifact，并用 Node 的 inventory/list 能力查看。
2. 核对模型、Variant、大小、状态、路径归属等用户可理解信息。
3. 删除一个明确属于 BurnCloud 的未运行 Artifact，确认文件和状态一致消失。
4. 尝试删除正在被 Runtime 使用的 Artifact 或非 BurnCloud-owned 文件。

**人类通过标准：** list/status 反映真实本地库存；删除只作用于明确 owned Artifact；in-use/ownership 不明时 fail closed；删除后不留下假 READY cache/state。

**人工判定失败：** 删除到无关文件、正在服务的 Artifact 被直接删掉、库存与磁盘事实不一致，或 cache cleanup 自己重新选择 Variant。

**建议证据：** 删除前后 inventory + 文件系统对比 + in-use 拒绝记录。

## NODE-400 — llama.cpp Runtime 自动可用

**验收者：** 产品负责人 + Runtime 工程师。

**人工步骤：**
1. 在没有手工配置 `llama-server` 路径的干净环境启动 Node。
2. 触发一个需要 llama.cpp 的本地模型。
3. 检查 Runtime 来源、版本、平台/backend、checksum/完整性和最终可用状态。

**人类通过标准：** 正常用户不需要自己安装/寻找 llama-server；BurnCloud 能准备一个受管理、可验证的 Runtime。

**人工判定失败：** 文档要求用户手工下载 binary、依赖 PATH 偶然存在的未知版本，或 Runtime 不匹配仍继续启动。

**建议证据：** 干净环境运行记录 + Runtime 元数据。

## NODE-401 — llama.cpp Runtime Adapter + ProcessSpec

**验收者：** Runtime 工程师。

**人工步骤：**
1. 给 Adapter 一个 READY Artifact + HardwareProfile。
2. 查看生成的 ProcessSpec。
3. 确认用户没有提供 GGUF 绝对路径、gpu_layers、内部端口或原始 CLI 参数。
4. 用明显非法配置验证明确失败。

**人类通过标准：** ProcessSpec 可执行、参数可解释、由 Runtime contract 产生，不把 PID/Child ownership混进 Runtime Adapter。

**人工判定失败：** 需要用户拼 CLI、Adapter 自己长期持有进程、或非法配置静默纠正成不可解释值。

**建议证据：** 一份有效 ProcessSpec + 一份非法配置失败。

## NODE-402 — 资源准入 / 内部端口 / Spawn

**验收者：** Runtime 工程师。

**人工步骤：**
1. 启动一个可运行模型，观察系统自动选择内部端口并 spawn。
2. 再启动第二模型，确认端口不冲突。
3. 制造资源不足和端口冲突场景。

**人类通过标准：** 用户不提供内部端口；资源不足在 spawn 前被拒绝；spawn 成功只表示 STARTING，不直接显示 READY。

**人工判定失败：** 固定端口撞车、资源不足仍 spawn、或 PID 出现就对外接流量。

**建议证据：** 两模型端口/PID记录 + 资源不足/冲突失败。

## NODE-403 — Readiness / Health

**验收者：** 产品负责人 + Runtime 工程师。

**人工步骤：**
1. 启动一个加载需要时间的模型，观察 `spawned → starting → ready` 过程。
2. 在 READY 前立即发真实请求，确认不会被路由进去。
3. 模拟 health endpoint 失败/超时。

**人类通过标准：** Readiness 成功后才 READY；Health 失败会明确降级/失败；真实流量永不进入未 READY Runtime。

**人工判定失败：** PID 创建即 READY、固定 sleep 代替 readiness、health 失败仍保持 routable。

**建议证据：** 状态时间线 + READY 前请求结果 + health failure 记录。

## NODE-404 — Stop / Crash / Restart / Logs

**验收者：** Runtime 工程师 + 运维负责人。

**人工步骤：**
1. 正常停止一个 managed Runtime，确认进程退出。
2. 强制杀掉一个 managed Runtime，观察 crash 检测和 restart policy。
3. 连续制造 crash 达到重启上限。
4. 查看 runtime logs 是否足够定位 exit code/失败原因。

**人类通过标准：** BurnCloud 对自己启动的模型进程负责清理；crash 可检测；restart 有上限；日志可诊断。

**人工判定失败：** Node 退出后 orphan process、无限 crash loop、失败被吞掉、或日志找不到具体 runtime/process 身份。

**建议证据：** process list 前后对比 + restart_count + 日志片段。

## NODE-501 — READY Runtime 自动注册 Local Channel

**验收者：** Router 工程师 + 产品负责人。

**人工步骤：**
1. 让一个本地 Runtime 真正进入 READY。
2. 查看现有 Channel/Ability 体系是否自动出现对应 Local candidate。
3. 通过正常 `/v1` 请求验证 ModelRouter 能选中它。

**人类通过标准：** Local 以现有 Channel/Ability 身份进入 Router，而不是旁路；未 READY 时绝不注册 routable candidate。

**人工判定失败：** 直接从 Gateway 调 localhost runtime、重复 Local Channel、或 STARTING 状态就被 Router 选中。

**建议证据：** READY 前后 Channel/Ability 对比 + `/v1` route trace。

## NODE-502 — Local Channel 健康联动 / 摘除 / 恢复

**验收者：** Router/Runtime 工程师。

**人工步骤：**
1. 在 Local READY 时确认请求可正常路由。
2. 人为让 Runtime unhealthy/crash。
3. 立即再次请求，确认 Local 不再被当作健康候选。
4. Runtime 恢复 READY 后确认 Local candidate 自动恢复。

**人类通过标准：** Channel 的 routable 状态跟随真实 Runtime health；失败时 fail closed，恢复后可重新进入 Router。

**人工判定失败：** Runtime 死掉后 Router 仍持续选 Local、需要人工删 Channel 才恢复，或恢复时创建重复 Channel。

**建议证据：** health/route 状态时间线。

## NODE-503 — Demand-driven 本地推理完整 E2E

**验收者：** 产品负责人必须参与，不能只由开发者签字。

**人工步骤：**
1. 客户端只提供 BurnCloud base URL、正常 credential、`model` 和正常请求 Body。
2. 验证 Local 已 READY 场景。
3. 验证 Local 不存在但 Provider 可用：第一请求立即 Provider 成功，同时后台准备 Local；Local READY 后后续请求自然转 Local。
4. 验证无 Provider 但本机可准备：先看到 `MODEL_PREPARING`，之后 retry 成功。
5. 验证 VRAM/Disk/Runtime 不可行时返回真实结构化原因。
6. 并发发送相同 model 请求，人工确认只有一套 Prepare/Runtime/Channel。

**人类通过标准：** 人全程不提供 GGUF path、artifact URL、llama-server path、内部端口、PID、gpu_layers、download task、start/stop 命令；仍可完成产品闭环。

**人工判定失败：** 任何成功步骤需要人工下载/启动/选文件/选端口；Provider 被迫等待本地下载；不可行状态被 generic model-not-found 掩盖；并发产生重复本地执行链。

**建议证据：** Scenario A~E 的完整请求/响应、route trace、状态变化记录。

## NODE-504 — Model Demand Reconciliation

**验收者：** 架构负责人 + 产品负责人。

**人工步骤：**
1. 对一个本地不存在的模型发送真实 `/v1` 请求。
2. 观察请求产生一个非阻塞 model demand。
3. 连续/并发重复请求，确认只存在一个 reconciliation pipeline。
4. 在 Provider 可用和不可用两种情况下观察当前请求与后台准备互不阻塞。
5. 重启 Node，确认 stale READY/Channel 不被盲目信任。

**人类通过标准：** Reconciler 只协调未来本地现实，不替代 ModelRouter；同 demand 去重；状态和失败原因可解释；重启 fail closed。

**人工判定失败：** Reconciler 自己选择当前 Channel、把下载/spawn 塞进 Router、Provider success 取消本地准备、或重启后信任不存在的进程。

**建议证据：** demand registry/state trace + 并发记录 + 重启前后状态。

---

## 人工签收记录建议

每个 Issue 合并前，PR 或 Engineering Issue 至少记录：

```text
Human Acceptance: PASS / FAIL
Accepted by: <human name / GitHub identity>
Environment: <OS / hardware / runtime / relevant provider>
Steps executed: <short list>
Evidence: <logs / screenshots / request-response / trace>
Known gaps: <none or explicit gaps>
```

如果人工验收无法执行，该 Issue 不应仅凭 AI review 或 CI 变成 DONE；应保持 `BLOCKED`、`IN PROGRESS`，或明确由架构负责人批准“为什么当前阶段只允许机器验收”。
