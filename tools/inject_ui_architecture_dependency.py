#!/usr/bin/env python3
"""Expose the BurnCloud UI Architecture Contract and bind every UI plan to it.

This runs after `tools/sanitize_mdx.py` has copied the hand-written BurnCloud UI
manual docs into `docs/` and generated `site/sidebars.js`.

It performs two governance operations:

1. Put the Architecture Contract in the BurnCloud UI sidebar before the
   Implementation Plan.
2. Inject an explicit mandatory Architecture dependency into the Implementation
   Plan index and every generated `UI-*` implementation page.

The inheritance rule remains canonical in `site/manual-docs/burncloud-ui/architecture/`;
this script makes that inheritance visible and machine-verifiable on every page.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "burncloud-ui"
PLAN_INDEX = DOC_ROOT / "implementation-plan.md"
PLAN_DIR = DOC_ROOT / "implementation-plan"
SIDEBAR = ROOT / "site" / "sidebars.js"

START_MARKER = "<!-- UI-ARCHITECTURE-DEPENDENCY: REQUIRED -->"
END_MARKER = "<!-- UI-ARCHITECTURE-DEPENDENCY: END -->"
BLOCK_RE = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER) + r"\n*",
    re.DOTALL,
)

DEPENDENCY_BLOCK = f"""{START_MARKER}
> **Mandatory Architecture Dependency（强制）**
>
> 本实施单元必须遵守 [BurnCloud UI Architecture Contract](/burncloud-ui/architecture/)。Architecture Contract 是本页、READY Engineering Issue、Task Contract 与 Production Dioxus 实现的上位约束。
>
> - 实施前必须读取 [Directory Contract](/burncloud-ui/architecture/directory-contract/)、[Authorization Contract](/burncloud-ui/architecture/authorization-contract/)、[API Boundary](/burncloud-ui/architecture/api-boundary/) 与 [Code Ownership](/burncloud-ui/architecture/code-ownership/) 中适用规则；
> - Task Contract 必须明确 `Allowed Paths / Conditional Paths / Forbidden Paths`；
> - 本页只能增加更严格的限制，**不能放宽 Architecture Contract**；
> - 若页面需求与 Architecture Contract 冲突，必须 `STOP → Architecture Dependency / Foundation Issue`，不得由 AI/Codex 自行扩大 scope 或修改 Protected Architecture Zone。
>
> `Implementation convenience != architecture authority`；`CI green != permission to violate the Architecture Contract`。
{END_MARKER}
"""

ARCHITECTURE_DOC_IDS = [
    "burncloud-ui/architecture/index",
    "burncloud-ui/architecture/overview",
    "burncloud-ui/architecture/directory-contract",
    "burncloud-ui/architecture/dependency-rules",
    "burncloud-ui/architecture/code-ownership",
    "burncloud-ui/architecture/route-contract",
    "burncloud-ui/architecture/authorization-contract",
    "burncloud-ui/architecture/api-boundary",
    "burncloud-ui/architecture/state-truth-contract",
    "burncloud-ui/architecture/shared-component-rules",
    "burncloud-ui/architecture/design-system",
    "burncloud-ui/architecture/i18n-contract",
    "burncloud-ui/architecture/css-contract",
    "burncloud-ui/architecture/platform-contract",
    "burncloud-ui/architecture/testing-contract",
    "burncloud-ui/architecture/ai-coding-boundaries",
    "burncloud-ui/architecture/architecture-lint",
    "burncloud-ui/architecture/migration-plan",
]


def inject_dependency(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = BLOCK_RE.sub("", text)

    # Put the mandatory parent contract immediately before the first H2 so it is
    # visible near the top without rewriting each plan's own content.
    h2 = re.search(r"^## ", text, re.MULTILINE)
    if h2:
        before = text[: h2.start()].rstrip()
        after = text[h2.start() :].lstrip()
        text = f"{before}\n\n{DEPENDENCY_BLOCK}\n{after}"
    else:
        text = f"{text.rstrip()}\n\n{DEPENDENCY_BLOCK}"

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def inject_plan_pages() -> list[Path]:
    if not PLAN_INDEX.is_file():
        raise RuntimeError("BurnCloud UI implementation-plan index not found")
    if not PLAN_DIR.is_dir():
        raise RuntimeError("BurnCloud UI implementation-plan directory not found")

    issues = sorted(PLAN_DIR.glob("ui-*.md"))
    if len(issues) < 34:
        raise RuntimeError(f"Expected at least 34 governed UI issues, found {len(issues)}")

    inject_dependency(PLAN_INDEX)
    for issue in issues:
        inject_dependency(issue)
    return issues


def patch_sidebar() -> None:
    text = SIDEBAR.read_text(encoding="utf-8")
    ui_start = "      {type:'category', label:'BurnCloud UI'"
    plan_anchor = (
        "        {type:'category', label:'实施计划', collapsed:false, "
        "link:{type:'doc', id:'burncloud-ui/implementation-plan'}, items:[\n"
    )

    if ui_start not in text:
        raise RuntimeError("BurnCloud UI sidebar category not found")
    if plan_anchor not in text:
        raise RuntimeError("BurnCloud UI implementation-plan sidebar anchor not found")

    architecture_block = """        {type:'category', label:'架构规范（必读）', collapsed:false, link:{type:'doc', id:'burncloud-ui/architecture/index'}, items:[
          {type:'doc', id:'burncloud-ui/architecture/overview', label:'Architecture Overview'},
          {type:'category', label:'代码结构与边界', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/architecture/directory-contract', label:'Directory Contract'},
            {type:'doc', id:'burncloud-ui/architecture/dependency-rules', label:'Dependency Rules'},
            {type:'doc', id:'burncloud-ui/architecture/code-ownership', label:'Code Ownership / 修改范围'},
          ]},
          {type:'category', label:'路由 / 权限 / API', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/architecture/route-contract', label:'Route Contract'},
            {type:'doc', id:'burncloud-ui/architecture/authorization-contract', label:'Authorization Contract'},
            {type:'doc', id:'burncloud-ui/architecture/api-boundary', label:'API Boundary'},
            {type:'doc', id:'burncloud-ui/architecture/state-truth-contract', label:'State Truth Contract'},
          ]},
          {type:'category', label:'UI 基础设施', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/architecture/shared-component-rules', label:'Shared Component Rules'},
            {type:'doc', id:'burncloud-ui/architecture/design-system', label:'Design System'},
            {type:'doc', id:'burncloud-ui/architecture/i18n-contract', label:'i18n Contract'},
            {type:'doc', id:'burncloud-ui/architecture/css-contract', label:'CSS Contract'},
            {type:'doc', id:'burncloud-ui/architecture/platform-contract', label:'Platform Contract'},
            {type:'doc', id:'burncloud-ui/architecture/testing-contract', label:'Testing Contract'},
          ]},
          {type:'category', label:'AI 与治理', collapsed:true, items:[
            {type:'doc', id:'burncloud-ui/architecture/ai-coding-boundaries', label:'AI Coding Boundaries'},
            {type:'doc', id:'burncloud-ui/architecture/architecture-lint', label:'Architecture Lint'},
            {type:'doc', id:'burncloud-ui/architecture/migration-plan', label:'Migration Plan'},
          ]},
        ]},
"""

    # Idempotence: sanitize_mdx regenerates the whole BurnCloud UI category, but
    # keep this safe if the injector is executed more than once in a local build.
    if "id:'burncloud-ui/architecture/index'" not in text:
        text = text.replace(plan_anchor, architecture_block + plan_anchor, 1)

    SIDEBAR.write_text(text, encoding="utf-8")


def verify(issues: list[Path]) -> None:
    for path in [PLAN_INDEX, *issues]:
        text = path.read_text(encoding="utf-8")
        if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
            raise RuntimeError(f"{path}: expected exactly one mandatory Architecture dependency block")
        for needle in [
            "/burncloud-ui/architecture/",
            "Allowed Paths / Conditional Paths / Forbidden Paths",
            "STOP → Architecture Dependency / Foundation Issue",
        ]:
            if needle not in text:
                raise RuntimeError(f"{path}: missing mandatory Architecture dependency text: {needle}")

    sidebar = SIDEBAR.read_text(encoding="utf-8")
    missing_ids = [doc_id for doc_id in ARCHITECTURE_DOC_IDS if f"id:'{doc_id}'" not in sidebar]
    if missing_ids:
        raise RuntimeError(f"Architecture docs missing from BurnCloud UI menu: {missing_ids}")

    architecture_pos = sidebar.index("id:'burncloud-ui/architecture/index'")
    implementation_pos = sidebar.index("id:'burncloud-ui/implementation-plan'")
    if architecture_pos >= implementation_pos:
        raise RuntimeError("Architecture Contract must appear before Implementation Plan in BurnCloud UI menu")

    print(f"ui_architecture_dependency_issues={len(issues)}")
    print(f"ui_architecture_menu_docs={len(ARCHITECTURE_DOC_IDS)}")
    print("ui_architecture_dependency=OK")


def main() -> None:
    issues = inject_plan_pages()
    patch_sidebar()
    verify(issues)


if __name__ == "__main__":
    main()
