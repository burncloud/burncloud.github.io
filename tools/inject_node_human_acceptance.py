#!/usr/bin/env python3
"""Inject canonical human acceptance criteria into generated BurnCloud Node issue pages.

Source of truth:
  site/manual-docs/burncloud-node/implementation-plan/human-acceptance.md

Targets:
  docs/burncloud-node/implementation-plan/node-NNN.md
  site/sidebars.js (only to expose NODE-004 / NODE-304 / Human Acceptance Registry)

The script is intentionally strict: every node-NNN page must have exactly one registry
entry, and every registry entry must map to an existing node-NNN page. This makes
"human acceptance missing" a documentation build failure instead of a review-time guess.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "site/manual-docs/burncloud-node/implementation-plan/human-acceptance.md"
DOC_DIR = ROOT / "docs/burncloud-node/implementation-plan"
SIDEBAR = ROOT / "site/sidebars.js"

HUMAN_MARKER = "## 第四层：人类验收（Human Acceptance）"
SOURCE_NOTE = (
    "> 本节由 [Node 人类验收标准]"
    "(/burncloud-node/implementation-plan/human-acceptance/) 生成。"
    "机器测试、CI 或 AI Review 不能替代这里的人工验收。"
)
SECTION_RE = re.compile(r"^## (NODE-\d{3})\s+—\s+(.+)$", re.MULTILINE)
FILE_RE = re.compile(r"node-(\d{3})\.md$")


def parse_registry() -> dict[str, tuple[str, str]]:
    text = REGISTRY.read_text(encoding="utf-8")
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        raise RuntimeError("No NODE-NNN human acceptance sections found")

    result: dict[str, tuple[str, str]] = {}
    for index, match in enumerate(matches):
        issue_id = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # The registry ends with a non-issue appendix. Keep it out of NODE-504.
        body = body.split("\n---\n\n## 人工签收记录建议", 1)[0].rstrip()
        if not body:
            raise RuntimeError(f"Empty human acceptance section: {issue_id}")
        if issue_id in result:
            raise RuntimeError(f"Duplicate human acceptance section: {issue_id}")
        result[issue_id] = (title, body)
    return result


def issue_files() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(DOC_DIR.glob("node-*.md")):
        match = FILE_RE.fullmatch(path.name)
        if not match:
            continue
        issue_id = f"NODE-{match.group(1)}"
        result[issue_id] = path
    return result


def inject_issue_pages(registry: dict[str, tuple[str, str]]) -> None:
    files = issue_files()
    missing_registry = sorted(set(files) - set(registry))
    missing_pages = sorted(set(registry) - set(files))
    if missing_registry or missing_pages:
        raise RuntimeError(
            "Human acceptance registry/page mismatch: "
            f"missing_registry={missing_registry}, missing_pages={missing_pages}"
        )

    for issue_id, path in files.items():
        title, body = registry[issue_id]
        text = path.read_text(encoding="utf-8")
        if HUMAN_MARKER in text:
            text = text.split(HUMAN_MARKER, 1)[0].rstrip()
            if text.endswith("---"):
                text = text[:-3].rstrip()

        injected = (
            f"{text}\n\n---\n\n{HUMAN_MARKER}\n\n{SOURCE_NOTE}\n\n"
            f"### {issue_id} — {title}\n\n{body}\n"
        )
        path.write_text(injected, encoding="utf-8")


def patch_sidebar() -> None:
    text = SIDEBAR.read_text(encoding="utf-8")

    issue_standard = (
        "          {type:'doc', id:'burncloud-node/implementation-plan/issue-standard', "
        "label:'Issue 标准'},\n"
    )
    human_acceptance = (
        "          {type:'doc', id:'burncloud-node/implementation-plan/human-acceptance', "
        "label:'人类验收标准'},\n"
    )
    if human_acceptance not in text:
        if issue_standard not in text:
            raise RuntimeError("Issue standard sidebar anchor not found")
        text = text.replace(issue_standard, issue_standard + human_acceptance, 1)

    node003 = (
        "            {type:'doc', id:'burncloud-node/implementation-plan/node-003', "
        "label:'NODE-003 复用 Server / Router'},\n"
    )
    node004 = (
        "            {type:'doc', id:'burncloud-node/implementation-plan/node-004', "
        "label:'NODE-004 Gateway / Protocol Compatibility'},\n"
    )
    if node004 not in text:
        if node003 not in text:
            raise RuntimeError("NODE-003 sidebar anchor not found")
        text = text.replace(node003, node003 + node004, 1)

    node303 = (
        "            {type:'doc', id:'burncloud-node/implementation-plan/node-303', "
        "label:'NODE-303 校验与失败恢复'},\n"
    )
    node304 = (
        "            {type:'doc', id:'burncloud-node/implementation-plan/node-304', "
        "label:'NODE-304 Inventory / Cache / Delete'},\n"
    )
    if node304 not in text:
        if node303 not in text:
            raise RuntimeError("NODE-303 sidebar anchor not found")
        text = text.replace(node303, node303 + node304, 1)

    SIDEBAR.write_text(text, encoding="utf-8")


def verify(registry: dict[str, tuple[str, str]]) -> None:
    files = issue_files()
    for issue_id, path in files.items():
        text = path.read_text(encoding="utf-8")
        if text.count(HUMAN_MARKER) != 1:
            raise RuntimeError(f"{path}: expected exactly one Human Acceptance section")
        for required in ["**验收者：**", "**人工步骤：**", "**人类通过标准：**", "**人工判定失败：**", "**建议证据：**"]:
            if required not in text:
                raise RuntimeError(f"{path}: missing {required}")

    if len(files) != len(registry):
        raise RuntimeError(f"Expected equal issue/registry count, got {len(files)} and {len(registry)}")

    print(f"node_human_acceptance_issues={len(files)}")
    print("node_human_acceptance=OK")


def main() -> None:
    registry = parse_registry()
    inject_issue_pages(registry)
    patch_sidebar()
    verify(registry)


if __name__ == "__main__":
    main()
