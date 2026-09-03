from pathlib import Path
import re
import shutil

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


def sync_burncloud_ui_docs() -> None:
    """Copy the hand-written BurnCloud UI product docs into generated docs."""
    source = ROOT / "site" / "manual-docs" / "burncloud-ui"
    target = DOCS / "burncloud-ui"
    if not source.is_dir():
        raise RuntimeError("BurnCloud UI manual docs source not found")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


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


def ensure_burncloud_ui_sidebar() -> None:
    """Expose the target BurnCloud UI docs with a canonical implementation-plan hierarchy."""
    text = SIDEBAR.read_text(encoding="utf-8")
    marker = "      {type:'doc', id:'burncloud-network/index', label:'BurnCloud Network'},\n"
    start_marker = "      {type:'category', label:'BurnCloud UI'"

    if marker not in text:
        raise RuntimeError("BurnCloud Network sidebar marker not found")

    # Replace an older injected BurnCloud UI block instead of appending a second copy.
    if start_marker in text:
        start = text.index(start_marker)
        end = text.index(marker, start)
        text = text[:start] + text[end:]

    block = """      {type:'category', label:'BurnCloud UI', collapsed:true, link:{type:'doc', id:'burncloud-ui/index'}, items:[
        {type:'category', label:'实施计划', collapsed:false, link:{type:'doc', id:'burncloud-ui/implementation-plan'}, items:[
          {type:'category', label:'Foundation', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-001', label:'UI-001 Target → Production Contract'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-002', label:'UI-002 Design Tokens + Components'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-007', label:'UI-007 i18n / Localization'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-003', label:'UI-003 Role/Auth Workspace'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-008', label:'UI-008 Console Namespace + Routes'},
          ]},
          {type:'category', label:'Buyer', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-001', label:'UI-BUYER-001 Overview'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-002', label:'UI-BUYER-002 Marketplace'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-003', label:'UI-BUYER-003 Playground'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-004', label:'UI-BUYER-004 API Keys'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-005', label:'UI-BUYER-005 Usage'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-006', label:'UI-BUYER-006 Billing'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-buyer-007', label:'UI-BUYER-007 Logs'},
          ]},
          {type:'category', label:'Supplier', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-001', label:'UI-SUPPLIER-001 Overview'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-002', label:'UI-SUPPLIER-002 Resources'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-003', label:'UI-SUPPLIER-003 Deployments'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-004', label:'UI-SUPPLIER-004 Reliability'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-005', label:'UI-SUPPLIER-005 Earnings'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-006', label:'UI-SUPPLIER-006 Settlements'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-supplier-007', label:'UI-SUPPLIER-007 Settings'},
          ]},
          {type:'category', label:'Admin', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-001', label:'UI-ADMIN-001 Overview'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-002', label:'UI-ADMIN-002 Supply'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-003', label:'UI-ADMIN-003 Capacity'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-004', label:'UI-ADMIN-004 Demand'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-005', label:'UI-ADMIN-005 Models'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-006', label:'UI-ADMIN-006 Operations'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-012', label:'UI-ADMIN-012 Billing'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-007', label:'UI-ADMIN-007 Revenue'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-008', label:'UI-ADMIN-008 Settlements'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-009', label:'UI-ADMIN-009 Suppliers'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-010', label:'UI-ADMIN-010 Customers'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-admin-011', label:'UI-ADMIN-011 Settings'},
          ]},
          {type:'category', label:'Cross-cutting / Release', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-004', label:'UI-004 Node Autopilot UX'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-005', label:'UI-005 Legacy Route Migration'},
            {type:'doc', id:'burncloud-ui/implementation-plan/ui-006', label:'UI-006 Final Quality Gate'},
          ]},
        ]},
        {type:'category', label:'Buyer', collapsed:true, link:{type:'doc', id:'burncloud-ui/buyer/index'}, items:[
          {type:'doc', id:'burncloud-ui/buyer/overview', label:'Overview'},
          {type:'doc', id:'burncloud-ui/buyer/playground', label:'Playground'},
          {type:'doc', id:'burncloud-ui/buyer/marketplace', label:'Marketplace'},
          {type:'doc', id:'burncloud-ui/buyer/api-keys', label:'API Keys'},
          {type:'doc', id:'burncloud-ui/buyer/usage', label:'Usage'},
          {type:'doc', id:'burncloud-ui/buyer/billing', label:'Billing'},
          {type:'doc', id:'burncloud-ui/buyer/logs', label:'Logs'},
        ]},
        {type:'category', label:'Supplier', collapsed:true, link:{type:'doc', id:'burncloud-ui/supplier/index'}, items:[
          {type:'doc', id:'burncloud-ui/supplier/overview', label:'Overview'},
          {type:'doc', id:'burncloud-ui/supplier/resources', label:'Resources'},
          {type:'doc', id:'burncloud-ui/supplier/deployments', label:'Deployments'},
          {type:'doc', id:'burncloud-ui/supplier/earnings', label:'Earnings'},
          {type:'doc', id:'burncloud-ui/supplier/settlements', label:'Settlements'},
          {type:'doc', id:'burncloud-ui/supplier/reliability', label:'Reliability'},
          {type:'doc', id:'burncloud-ui/supplier/settings', label:'Settings'},
        ]},
        {type:'category', label:'Admin', collapsed:true, link:{type:'doc', id:'burncloud-ui/admin/index'}, items:[
          {type:'doc', id:'burncloud-ui/admin/overview', label:'Overview'},
          {type:'doc', id:'burncloud-ui/admin/supply', label:'Supply'},
          {type:'doc', id:'burncloud-ui/admin/capacity', label:'Capacity'},
          {type:'doc', id:'burncloud-ui/admin/demand', label:'Demand'},
          {type:'doc', id:'burncloud-ui/admin/models', label:'Models'},
          {type:'doc', id:'burncloud-ui/admin/operations', label:'Operations'},
          {type:'doc', id:'burncloud-ui/admin/billing', label:'Billing'},
          {type:'doc', id:'burncloud-ui/admin/revenue', label:'Revenue'},
          {type:'doc', id:'burncloud-ui/admin/settlements', label:'Settlements'},
          {type:'doc', id:'burncloud-ui/admin/suppliers', label:'Suppliers'},
          {type:'doc', id:'burncloud-ui/admin/customers', label:'Customers'},
          {type:'doc', id:'burncloud-ui/admin/settings', label:'Settings'},
        ]},
      ]},
"""

    SIDEBAR.write_text(text.replace(marker, block + marker, 1), encoding="utf-8")


def localize_sidebar_labels() -> None:
    """Use Chinese navigation labels while preserving API paths and code identifiers."""
    text = SIDEBAR.read_text(encoding="utf-8")
    translations = {
        "BurnCloud Node": "BurnCloud 节点",
        "BurnCloud UI": "BurnCloud 界面",
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
sync_burncloud_ui_docs()
build_sidebar()
ensure_node_implementation_plan_sidebar()
ensure_burncloud_ui_sidebar()
localize_sidebar_labels()
print("Injected curated BurnCloud product docs with Node and UI product hierarchies before MDX sanitization")

changed = 0
for md in DOCS.rglob("*.md"):
    if sanitize(md):
        changed += 1

print(f"Sanitized {changed} Markdown files for MDX")
