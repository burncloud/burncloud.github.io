#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "## 一句话先看懂",
    "## 这次主要改了什么",
    "## 10 个修改维度",
    "## 1. 修改范围",
    "## 2. 用户流程",
    "## 3. 运行过程",
    "## 4. 控制流程",
    "## 5. 状态变化",
    "## 6. API 契约",
    "## 7. 数据库 / 持久化",
    "## 8. 外部依赖",
    "## 9. 影响范围",
    "## 10. 测试与证据",
    "## 风险判断",
    "## 程序员 Review 清单",
    "## 直接看源码",
]

EVIDENCE_RE = re.compile(
    r"^- \*\*(?:修改前|修改后|BASE|AFTER):\*\* "
    r"\[`[^`]+`\]\(https://github\.com/burncloud/burncloud/blob/"
    r"([0-9a-f]{40})/([^\s)#]+)#L(\d+)-L(\d+)\)$",
    re.M,
)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def git(repo: Path, *args: str, check=True):
    p = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout


def parse_frontmatter(text: str):
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def lines_at(repo: Path, sha: str, path: str):
    p = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        return None
    return p.stdout.decode("utf-8", "replace").splitlines()


def section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    if next_heading:
        end = text.find(next_heading, start + len(heading))
        if end >= 0:
            return text[start:end]
    return text[start:]


def validate(docs: Path, repo: Path):
    errors = []
    index_path = docs / "commit-index.json"
    if not index_path.exists():
        return ["missing docs/commit-index.json"]

    records = json.loads(index_path.read_text(encoding="utf-8"))
    if len(records) != 30:
        errors.append(f"expected exactly 30 records, got {len(records)}")
    targets = [r.get("target") for r in records]
    if len(set(targets)) != len(targets):
        errors.append("duplicate target commits in index")

    md_files = sorted((docs / "commits").glob("*.md"))
    if len(md_files) != 30:
        errors.append(f"expected exactly 30 commit Markdown files, got {len(md_files)}")
    json_files = sorted((docs / "commits").glob("*.json"))
    if len(json_files) != 31:
        errors.append(f"expected 31 JSON files in commits/ including category, got {len(json_files)}")

    rec_by_doc = {r.get("doc"): r for r in records}
    evidence_checked = 0
    text_graphs = 0
    semantic_units_total = 0

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        rec = rec_by_doc.get(md.name)
        if not rec:
            errors.append(f"{md.name}: missing machine-readable index record")
            continue

        for k in ["doc_type", "repository", "pr_number", "base_commit", "target_commit", "risk", "merged_at", "language", "diagram_style"]:
            if not fm.get(k):
                errors.append(f"{md.name}: missing frontmatter {k}")
        if fm.get("doc_type") != "commit-change-atlas-v2":
            errors.append(f"{md.name}: wrong doc_type {fm.get('doc_type')}")
        if fm.get("language") != "zh-CN":
            errors.append(f"{md.name}: language must be zh-CN")
        if fm.get("diagram_style") != "plaintext":
            errors.append(f"{md.name}: diagram_style must be plaintext")

        base = fm.get("base_commit", "")
        target = fm.get("target_commit", "")
        if re.fullmatch(r"[0-9a-f]{40}", target or ""):
            parents = git(repo, "show", "-s", "--format=%P", target, check=False).strip().split()
            if not parents:
                errors.append(f"{md.name}: target commit unavailable: {target}")
            elif base != parents[0]:
                errors.append(f"{md.name}: base {base} is not first parent {parents[0]} of target {target}")
        else:
            errors.append(f"{md.name}: invalid target commit")

        for heading in REQUIRED:
            n = text.count(heading)
            if n != 1:
                errors.append(f"{md.name}: heading {heading!r} count={n}, expected 1")

        # V2 reading model: semantic change units first, 10 dimensions later.
        units = rec.get("semantic_units") or []
        semantic_units_total += len(units)
        if not (1 <= len(units) <= 5):
            errors.append(f"{md.name}: expected 1..5 semantic change units, got {len(units)}")
        unit_headings = len(re.findall(r"^### 变化 \d+：", text, re.M))
        if unit_headings != len(units):
            errors.append(f"{md.name}: semantic unit heading count={unit_headings}, record count={len(units)}")
        blocks = re.findall(r"```text\n(.*?)```", text, re.S)
        text_graphs += len(blocks)
        if len(blocks) < len(units):
            errors.append(f"{md.name}: needs >=1 plaintext graph per semantic unit; graphs={len(blocks)}, units={len(units)}")
        if "```mermaid" in text:
            errors.append(f"{md.name}: V2 commit docs must not contain Mermaid")

        # Reject old generator vocabulary that signaled the broken keyword-first reading model.
        for old in ["## 1. Change Scope", "## 2. User Flow Impact", "## 3. End-to-End Runtime Diff", "STATIC CONFIRMED"]:
            if old in text:
                errors.append(f"{md.name}: old V1 presentation leaked into V2: {old}")

        # 10 dimensions must exist exactly once in dashboard records.
        dims = rec.get("dimensions") or {}
        if set(dims) != {str(i) for i in range(1, 11)}:
            errors.append(f"{md.name}: machine record must contain dimensions 1..10 exactly")
        dashboard = section(text, "## 10 个修改维度", "## 1. 修改范围")
        for i in range(1, 11):
            if f"| {i}." not in dashboard:
                errors.append(f"{md.name}: dashboard missing dimension {i}")

        # Historical evidence must bind to immutable SHA and valid historical lines.
        for line in text.splitlines():
            if (line.startswith("- **修改前:") or line.startswith("- **修改后:") or line.startswith("- **BASE:") or line.startswith("- **AFTER:")) and "blob/main/" in line:
                errors.append(f"{md.name}: generated evidence must never bind to main")
        for sha, path, a, b in EVIDENCE_RE.findall(text):
            evidence_checked += 1
            a, b = int(a), int(b)
            lines = lines_at(repo, sha, path.replace("%20", " "))
            if lines is None:
                errors.append(f"{md.name}: missing historical evidence file {sha}:{path}")
                continue
            if not (1 <= a <= b <= len(lines)):
                errors.append(f"{md.name}: bad evidence range {sha}:{path}:L{a}-L{b}; file has {len(lines)} lines")

        if "AUTHOR-STATED INTENT" not in text:
            errors.append(f"{md.name}: author-stated intent source must be explicit")

    # Golden regression: #352 exposed the exact semantic failures that triggered V2.
    golden = next((p for p in md_files if "pr-352-5c0772ce" in p.name), None)
    if not golden:
        errors.append("golden sample PR #352 not found in latest 30")
    else:
        g = golden.read_text(encoding="utf-8")
        required_gold = ["登录和鉴权", "SQLite", "弹窗", "BCModal"]
        for x in required_gold:
            if x not in g:
                errors.append(f"golden #352: missing required semantic concept {x!r}")
        for forbidden in ["Chat Completion", "Streaming Response", "Passthrough"]:
            if forbidden in g:
                errors.append(f"golden #352: forbidden false runtime mapping leaked: {forbidden}")
        api_sec = section(g, "## 6. API 契约", "## 7. 数据库 / 持久化")
        if "没发现服务器公开 API 契约变化" not in api_sec:
            errors.append("golden #352: client Bearer-header behavior must not be promoted to public API contract change")
        db_sec = section(g, "## 7. 数据库 / 持久化", "## 8. 外部依赖")
        for bad in ["select-none", "user-select"]:
            if bad in db_sec:
                errors.append(f"golden #352: CSS leaked into database analysis: {bad}")
        if "```mermaid" in g:
            errors.append("golden #352: must use plaintext, not Mermaid")

    if evidence_checked < 30:
        errors.append(f"too few historical evidence links checked: {evidence_checked}")

    print(f"Commit docs: {len(md_files)}")
    print(f"Semantic change units: {semantic_units_total}")
    print(f"Plaintext graphs: {text_graphs}")
    print(f"Historical evidence links checked: {evidence_checked}")
    if golden and not any(e.startswith("golden #352") for e in errors):
        print("Golden sample PR #352: PASS")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs", type=Path)
    ap.add_argument("source_repo", type=Path)
    a = ap.parse_args()
    errors = validate(a.docs.resolve(), a.source_repo.resolve())
    if errors:
        print("ERRORS:")
        for e in errors:
            print("-", e)
        sys.exit(1)
    print("OK: 30 commits × Chinese semantic units × plaintext graphs × 10 dimensions validation passed")


if __name__ == "__main__":
    main()
