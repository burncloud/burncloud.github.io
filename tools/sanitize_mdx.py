from pathlib import Path
import re

from generate_product_docs import build_sidebar, copy_manual_docs

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SIDEBAR = ROOT / "site" / "sidebars.js"

INLINE_CODE = re.compile(r"(`[^`]*`)")


def escape_text(fragment: str) -> str:
    # Generated docs deliberately use literal CLI placeholders such as <model>
    # and route placeholders such as {*path}. Outside code spans/fences MDX
    # interprets those as JSX / expressions, so encode them as HTML entities.
    return (
        fragment
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
    )


def sanitize_inline_content(line: str) -> str:
    prefix = ""
    body = line
    if body.startswith("> "):
        prefix, body = "> ", body[2:]
    elif body.startswith(">"):
        prefix, body = ">", body[1:]

    parts = INLINE_CODE.split(body)
    for idx in range(0, len(parts), 2):
        parts[idx] = escape_text(parts[idx])
    return prefix + "".join(parts)


def sanitize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    in_frontmatter = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if i == 0 and stripped == "---":
            in_frontmatter = True
            out.append(line)
            continue
        if in_frontmatter:
            out.append(line)
            if stripped == "---":
                in_frontmatter = False
            continue

        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        out.append(sanitize_inline_content(line))

    new = "".join(out)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def ensure_node_implementation_plan_sidebar() -> None:
    """Inject the curated, categorized BurnCloud Node implementation plan."""
    text = SIDEBAR.read_text(encoding="utf-8")
    marker = "        {type:'doc', id:'burncloud-node/local-api-gateway', label:'Local API Gateway'},\n"

    if "id:'burncloud-node/implementation-plan/node-504'" in text:
        return
    if marker not in text:
        raise RuntimeError("BurnCloud Node sidebar marker not found")

    block = """        {type:'category', label:'实施计划', collapsed:false, link:{type:'doc', id:'burncloud-node/implementation-plan'}, items:[
          {type:'doc', id:'burncloud-node/implementation-plan/issue-standard', label:'Issue 标准'},
          {type:'category', label:'类别一：Node Core', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/node-core'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-001', label:'NODE-001 启动入口与生命周期'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-002', label:'NODE-002 配置与共享上下文'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-003', label:'NODE-003 复用 Server / Router'},
          ]},
          {type:'category', label:'类别二：Hardware Profile', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/hardware-profile'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-101', label:'NODE-101 canonical HardwareProfile'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-102', label:'NODE-102 NVIDIA GPU 检测'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-103', label:'NODE-103 兼容性与资源快照'},
          ]},
          {type:'category', label:'类别三：Model Resolver', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/model-resolver'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-201', label:'NODE-201 Model Manifest + Catalog'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-202', label:'NODE-202 Model ID / Alias'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-203', label:'NODE-203 Variant 选择与诊断'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-204', label:'NODE-204 ResolvedModel / Failure 合同'},
          ]},
          {type:'category', label:'类别四：Model Preparation', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/model-preparation'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-301', label:'NODE-301 Local Artifact State'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-302', label:'NODE-302 后台 Prepare / 磁盘准入 / 去重'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-303', label:'NODE-303 校验与失败恢复'},
          ]},
          {type:'category', label:'类别五：Runtime 与 Process', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/runtime-process'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-400', label:'NODE-400 llama.cpp Runtime 自动可用'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-401', label:'NODE-401 llama.cpp Runtime Adapter'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-402', label:'NODE-402 资源准入 / 端口 / Spawn'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-403', label:'NODE-403 Readiness / Health'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-404', label:'NODE-404 自动 Stop / Crash / Restart / Logs'},
          ]},
          {type:'category', label:'类别六：Local Channel + Demand', collapsed:true, link:{type:'doc', id:'burncloud-node/implementation-plan/local-channel'}, items:[
            {type:'doc', id:'burncloud-node/implementation-plan/node-501', label:'NODE-501 READY 自动注册 Local Channel'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-502', label:'NODE-502 健康联动与摘除'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-504', label:'NODE-504 Model Demand Reconciliation'},
            {type:'doc', id:'burncloud-node/implementation-plan/node-503', label:'NODE-503 Demand-driven 完整 E2E'},
          ]},
        ]},
"""

    SIDEBAR.write_text(text.replace(marker, block + marker, 1), encoding="utf-8")


def localize_sidebar_labels() -> None:
    """Use Chinese navigation labels while preserving API paths and code identifiers."""
    text = SIDEBAR.read_text(encoding="utf-8")
    translations = {
        "BurnCloud Node": "BurnCloud 节点",
        "Local API Gateway": "本地 API 网关",
        "Protocol Routing": "协议路由",
        "Hardware Detection": "硬件检测",
        "Model Resolver": "模型解析",
        "Model Manager": "模型管理",
        "Runtime Manager": "运行时管理",
        "Process Manager": "进程管理",
        "BurnCloud Network": "BurnCloud 网络",
        "Technical Reference": "技术参考",
        "AI API / Data Plane": "AI API / 数据面",
        "Authentication": "身份认证",
        "Channel Management": "渠道管理",
        "Token": "Token 管理",
        "User": "用户",
        "Billing / Usage": "计费 / 用量",
        "Logs": "日志",
        "Monitoring / Security": "监控 / 安全",
        "Cache": "缓存",
        "Admin / Internal": "管理 / 内部",
        "CLI / Executables": "CLI / 可执行程序",
        "Background Jobs": "后台任务",
        "Startup": "启动流程",
        "UI-only Actions": "仅 UI 操作",
        "PR Change Atlas（最近 50 条）": "PR 变更图谱（最近 50 条）",
    }

    for source, target in translations.items():
        text = text.replace(f"label:'{source}'", f"label:'{target}'")
        text = text.replace(f'label:"{source}"', f'label:"{target}"')

    SIDEBAR.write_text(text, encoding="utf-8")


copy_manual_docs()
build_sidebar()
ensure_node_implementation_plan_sidebar()
localize_sidebar_labels()
print("Injected curated BurnCloud product docs with categorized Node issue plan before MDX sanitization")

changed = 0
for md in DOCS.rglob("*.md"):
    if sanitize(md):
        changed += 1

print(f"Sanitized {changed} Markdown files for MDX")
