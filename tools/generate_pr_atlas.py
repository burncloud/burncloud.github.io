from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SIDEBAR = ROOT / "site" / "sidebars.js"
SOURCE_REPO = "burncloud/burncloud"
API = "https://api.github.com"


def request_json(url: str):
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "burncloud-pr-change-atlas",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # A repository-scoped Actions token may not be accepted for another repo.
        # Public BurnCloud metadata is still readable anonymously, so retry once.
        if token and e.code in (401, 403, 404):
            headers.pop("Authorization", None)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        raise


def fetch_recent_prs(limit: int):
    q = urllib.parse.urlencode({
        "state": "all",
        "sort": "created",
        "direction": "desc",
        "per_page": min(limit, 100),
    })
    prs = request_json(f"{API}/repos/{SOURCE_REPO}/pulls?{q}")
    return prs[:limit]


def fetch_pr_files(number: int):
    out = []
    page = 1
    while True:
        url = f"{API}/repos/{SOURCE_REPO}/pulls/{number}/files?per_page=100&page={page}"
        batch = request_json(url)
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def section_text(text: str, heading: str) -> str:
    m = re.search(rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text)
    return m.group(1).strip() if m else ""


def first_fence(text: str, lang: str | None = None) -> tuple[str, str]:
    if lang:
        m = re.search(rf"(?ms)```{re.escape(lang)}\s*\n(.*?)\n```", text)
    else:
        m = re.search(r"(?ms)```([A-Za-z0-9_-]*)\s*\n(.*?)\n```", text)
        if m:
            return m.group(1) or "text", m.group(2)
    if not m:
        return "", ""
    return lang or "text", m.group(1)


def extract_source_paths(text: str) -> list[str]:
    sec = section_text(text, "穿过的源码文件（详细）")
    if not sec:
        sec = section_text(text, "穿过的源码文件")
    paths = re.findall(r"\|\s*\d+\s*\|\s*`([^`]+)`\s*\|", sec)
    # V4 pages may also mention exact FILE: paths in the flow that are not repeated in the table.
    flow_sec = section_text(text, "End-to-End Request Flow + ICFG")
    for p in re.findall(r"FILE:\s+([^\s+]+)", flow_sec):
        p = p.strip().rstrip(".,")
        if "/" in p and p not in paths:
            paths.append(p)
    return paths


def load_atlas_pages():
    manifest = json.loads((DOCS / "atlas-manifest.json").read_text(encoding="utf-8"))
    pages = []
    for meta in manifest["pages"]:
        path = DOCS / (meta["docid"] + ".md")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        flow_sec = section_text(text, "End-to-End Request Flow + ICFG")
        _, flow = first_fence(flow_sec, "text")
        if not flow:
            continue
        output_sec = section_text(text, "返回结果示例")
        out_lang, out_body = first_fence(output_sec)
        pages.append({
            **meta,
            "path": path,
            "source_paths": extract_source_paths(text),
            "flow": flow,
            "output_lang": out_lang,
            "output": out_body,
        })
    return manifest, pages


def path_matches(atlas_path: str, changed: str) -> bool:
    atlas_path = atlas_path.strip()
    if atlas_path.endswith("/*"):
        return changed.startswith(atlas_path[:-1])
    return atlas_path == changed


def flow_changed_files(page, changed_names: set[str]) -> list[str]:
    out = []
    for ap in page["source_paths"]:
        for cf in changed_names:
            if path_matches(ap, cf) and cf not in out:
                out.append(cf)
    return out


def annotate_flow(flow: str, changed: list[str]) -> str:
    if not changed:
        return flow
    lines = []
    for line in flow.splitlines():
        marked = any(cf in line for cf in changed)
        if marked and "[PR CHANGED]" not in line:
            line += "  [PR CHANGED]"
        lines.append(line)
    return "\n".join(lines)


def classify_change(files: list[dict]) -> str:
    names = [f["filename"] for f in files]
    if names and all(n.startswith(("docs/", ".github/")) or n.endswith((".md", ".yml", ".yaml")) for n in names):
        return "DOCS / CI ONLY"
    if names and all("test" in n.lower() or n.startswith("crates/tests/") for n in names):
        return "TEST ONLY"
    runtime = any(n.endswith(".rs") and not ("test" in n.lower() or n.startswith("crates/tests/")) for n in names)
    ui = any("client" in n and n.endswith(".rs") for n in names)
    db = any("database" in n or "migration" in n for n in names)
    bits = []
    if runtime:
        bits.append("RUNTIME")
    if ui:
        bits.append("UI")
    if db:
        bits.append("STATE/DB")
    return " + ".join(bits) if bits else "SOURCE / TOOLING"


def body_excerpt(body: str | None, limit: int = 1400) -> str:
    if not body:
        return "PR 未提供正文说明。"
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body[:limit] + ("…" if len(body) > limit else "")


def patch_highlights(file: dict, max_each: int = 8):
    patch = file.get("patch") or ""
    before, after = [], []
    for line in patch.splitlines():
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("-") and len(before) < max_each:
            before.append(line)
        elif line.startswith("+") and len(after) < max_each:
            after.append(line)
    hunks = re.findall(r"^@@.*@@.*$", patch, flags=re.M)[:6]
    return before, after, hunks


def esc_table(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_pr(pr: dict, files: list[dict], pages: list[dict], source_sha: str) -> str:
    number = pr["number"]
    changed_names = {f["filename"] for f in files}
    impacted = []
    mapped_files = set()
    for page in pages:
        hits = flow_changed_files(page, changed_names)
        if hits:
            impacted.append((page, hits))
            mapped_files.update(hits)

    additions = sum(int(f.get("additions", 0)) for f in files)
    deletions = sum(int(f.get("deletions", 0)) for f in files)
    merged = bool(pr.get("merged_at"))
    status = "MERGED" if merged else ("OPEN" if pr.get("state") == "open" else "CLOSED / NOT MERGED")
    base_sha = (pr.get("base") or {}).get("sha", "")
    head_sha = (pr.get("head") or {}).get("sha", "")
    base_ref = (pr.get("base") or {}).get("ref", "")
    head_ref = (pr.get("head") or {}).get("ref", "")
    author = (pr.get("user") or {}).get("login", "unknown")

    out = []
    out.append("---")
    out.append(f"title: \"PR #{number} — {str(pr.get('title','')).replace(chr(34), chr(39))}\"")
    out.append(f"slug: /pr/pr-{number}")
    out.append("---\n")
    out.append(f"# PR #{number} — {pr.get('title','')}\n")
    out.append(f"> **状态：** {status}  ")
    out.append(f"> **作者：** `{author}`  ")
    out.append(f"> **创建：** `{pr.get('created_at','')}`  ")
    out.append(f"> **Base：** `{base_ref}@{base_sha[:12]}`  ")
    out.append(f"> **Head：** `{head_ref}@{head_sha[:12]}`  ")
    out.append(f"> **完整 E2E 拓扑基线：** `burncloud/burncloud@{source_sha}`  ")
    out.append("> **证据规则：** PR changed files / patch 为 `STATIC CONFIRMED`；下方完整 E2E 使用当前已审计 Atlas 拓扑，并在命中 PR changed file 的节点标记 `[PR CHANGED]`。旧 PR 的历史 head 可能与当前拓扑存在后续演化，因此未把当前拓扑伪装成历史源码逐行复现。\n")

    out.append("## PR 影响总览\n")
    out.append(f"- **Change Class：** `{classify_change(files)}`")
    out.append(f"- **Changed Files：** `{len(files)}`")
    out.append(f"- **Additions / Deletions：** `+{additions} / -{deletions}`")
    out.append(f"- **受影响的完整 E2E Flow：** `{len(impacted)}`")
    out.append(f"- **未映射 changed files：** `{len(changed_names - mapped_files)}`\n")
    out.append("**PR 说明摘要：** " + body_excerpt(pr.get("body")) + "\n")

    out.append("## Changed Files\n")
    out.append("| 文件 | 状态 | + | - | Atlas 命中 |")
    out.append("|---|---:|---:|---:|---:|")
    for f in files:
        name = f["filename"]
        hit_count = sum(1 for _, hits in impacted if name in hits)
        out.append(f"| `{esc_table(name)}` | {f.get('status','')} | {f.get('additions',0)} | {f.get('deletions',0)} | {hit_count} |")
    out.append("")

    out.append("## Affected E2E Impact Matrix\n")
    if impacted:
        out.append("| # | 完整 E2E / Entry Point | 类型 | PR 命中的源码文件 |")
        out.append("|---:|---|---|---|")
        for i, (p, hits) in enumerate(impacted, 1):
            out.append(f"| {i} | `{esc_table(p.get('title') or p.get('entry'))}` | {esc_table(p.get('section',''))} / {esc_table(p.get('group',''))} | " + "<br/>".join(f"`{esc_table(x)}`" for x in hits) + " |")
    else:
        out.append("当前 PR 的 changed files 与当前 204+ 页 Atlas 的已审计源码路径没有精确交集，因此本页**不会虚构受影响 E2E**。这通常表示 docs/test/CI-only 变更，或旧 PR 使用了当前基线已经重命名/删除的路径。")
    out.append("")

    out.append("## 完整受影响 E2E Request Flow\n")
    if not impacted:
        out.append("**Affected Runtime E2E: NONE CONFIRMED BY CURRENT ATLAS PATH MAPPING.**\n")
    for i, (p, hits) in enumerate(impacted, 1):
        title = p.get("title") or p.get("entry")
        out.append(f"### E2E FLOW #{i} — {title}\n")
        out.append(f"**树路径：** `{p.get('section','')} → {p.get('group','')} → {title}`  ")
        out.append("**PR Impact：** `STATIC SOURCE-PATH MATCH`  ")
        out.append("**本 Flow 命中的 changed files：** " + ", ".join(f"`{x}`" for x in hits) + "\n")
        out.append("```text")
        out.append(annotate_flow(p["flow"], hits))
        out.append("```\n")

        out.append("#### PR Before / After（patch 证据）\n")
        relevant = [f for f in files if f["filename"] in hits]
        for f in relevant:
            before, after, hunks = patch_highlights(f)
            out.append(f"**FILE: `{f['filename']}`**")
            if hunks:
                out.append("\nHUNKS:")
                out.append("```text")
                out.extend(hunks)
                out.append("```")
            if before:
                out.append("\nBEFORE / REMOVED:")
                out.append("```diff")
                out.extend(before)
                out.append("```")
            if after:
                out.append("\nAFTER / ADDED:")
                out.append("```diff")
                out.extend(after)
                out.append("```")
            if not (before or after or hunks):
                out.append("\nPatch 内容不可用（可能是二进制、超大 diff 或 GitHub 未返回 patch）。")
            out.append("")

        if p.get("output"):
            out.append("#### 当前 Atlas 返回结果基线\n")
            out.append("> 这是当前审计基线的结果示例，不代表该历史 PR 的 response 一定完全相同；PR-specific response 变化以 patch 证据为准。\n")
            out.append(f"```{p.get('output_lang') or 'text'}")
            out.append(p["output"])
            out.append("```\n")

    unmapped = sorted(changed_names - mapped_files)
    out.append("## 未映射 Changed Files\n")
    if unmapped:
        for name in unmapped:
            out.append(f"- `{name}`")
    else:
        out.append("无。所有 changed files 均至少命中一条当前 Atlas 源码路径。")
    out.append("")

    out.append("## Execution Classification\n")
    out.append("- **PR metadata / changed filenames / patch hunks：STATIC CONFIRMED**")
    out.append("- **Affected Flow 判定：STATIC CONFIRMED（当前 Atlas source-path 精确交集）**")
    out.append("- **完整 Flow 拓扑：CURRENT AUDITED BASELINE**")
    out.append("- **历史 PR head 的逐行精确 Runtime 拓扑：NOT CLAIMED，除非 patch 本身直接证明**")
    out.append("")
    return "\n".join(out)


def update_sidebar(prs: list[dict]):
    text = SIDEBAR.read_text(encoding="utf-8")
    start = "    // PR_CHANGE_ATLAS_START\n"
    end = "    // PR_CHANGE_ATLAS_END\n"
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)
    items = []
    for pr in prs:
        label = f"#{pr['number']} {pr.get('title','')}"
        if len(label) > 76:
            label = label[:73] + "..."
        label = label.replace("\\", "\\\\").replace('"', '\\"')
        items.append(f'      {{type:\'doc\', id:"pr/pr-{pr["number"]}", label:"{label}"}},')
    block = start
    block += "    {type:'category', label:\"PR Change Atlas（最近 50 条）\", collapsed:false, items:[\n"
    block += "\n".join(items) + "\n"
    block += "    ]},\n"
    block += end
    marker = "  docsSidebar: [\n"
    if marker not in text:
        raise RuntimeError("docsSidebar marker not found")
    text = text.replace(marker, marker + block, 1)
    SIDEBAR.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    if args.limit < 1 or args.limit > 100:
        raise SystemExit("--limit must be 1..100")

    manifest, pages = load_atlas_pages()
    prs = fetch_recent_prs(args.limit)
    if len(prs) != args.limit:
        raise RuntimeError(f"expected {args.limit} PRs, got {len(prs)}")

    pr_dir = DOCS / "pr"
    if pr_dir.exists():
        shutil.rmtree(pr_dir)
    pr_dir.mkdir(parents=True)

    index_rows = []
    for pr in prs:
        files = fetch_pr_files(pr["number"])
        md = render_pr(pr, files, pages, manifest["source_sha"])
        path = pr_dir / f"pr-{pr['number']}.md"
        path.write_text(md, encoding="utf-8")
        index_rows.append({
            "number": pr["number"],
            "title": pr.get("title", ""),
            "state": pr.get("state"),
            "merged_at": pr.get("merged_at"),
            "created_at": pr.get("created_at"),
            "changed_files": len(files),
        })

    update_sidebar(prs)
    (DOCS / "pr-atlas-manifest.json").write_text(json.dumps({
        "source_repo": SOURCE_REPO,
        "atlas_source_sha": manifest["source_sha"],
        "pr_count": len(prs),
        "prs": index_rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(prs)} PR Change Atlas pages under docs/pr/")


if __name__ == "__main__":
    main()
