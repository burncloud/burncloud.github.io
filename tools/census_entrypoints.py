from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from collections import Counter, defaultdict

METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH")
METHOD_FN = {"get":"GET","post":"POST","put":"PUT","delete":"DELETE","patch":"PATCH"}


def iter_route_calls(text: str):
    """Yield .route(...) call bodies with a tiny balanced-paren scanner."""
    needle = ".route("
    pos = 0
    while True:
        start = text.find(needle, pos)
        if start < 0:
            return
        i = start + len(needle)
        depth = 1
        in_string = False
        escape = False
        while i < len(text) and depth:
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            i += 1
        if depth == 0:
            yield start, text[start + len(needle): i - 1]
            pos = i
        else:
            return


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def normalize_path(path: str) -> str:
    # Dioxus dynamic names and Axum dynamic names are semantically equivalent
    # for coverage purposes; keep wildcards distinct.
    path = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", r"{\1}", path)
    return path


def parse_http_routes(source: Path):
    found = []
    for f in source.rglob("*.rs"):
        rel = f.relative_to(source).as_posix()
        if "/target/" in f"/{rel}/":
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for offset, body in iter_route_calls(text):
            m = re.match(r'\s*"([^"]+)"\s*,(.*)', body, re.S)
            if not m:
                continue
            path, expr = normalize_path(m.group(1)), m.group(2)
            methods = []
            for fn, method in METHOD_FN.items():
                if re.search(rf"(?:\b|::){fn}\s*\(", expr):
                    methods.append(method)
            if not methods:
                # Route may use method_router variables or other Axum forms.
                methods = ["UNKNOWN"]
            handlers = sorted(set(re.findall(r"(?:get|post|put|delete|patch)\s*\(\s*([A-Za-z_][A-Za-z0-9_:]*)", expr)))
            for method in methods:
                found.append({
                    "method": method,
                    "path": path,
                    "entry": f"{method} {path}",
                    "file": rel,
                    "line": line_no(text, offset),
                    "handlers": handlers,
                })
    # top-level route_service/fallback are not endpoint pages but are useful audit facts
    return found


def parse_dioxus_routes(source: Path):
    found = []
    for f in source.rglob("*.rs"):
        rel = f.relative_to(source).as_posix()
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'#\[route\(\s*"([^"]+)"\s*\)\]', text):
            found.append({"path": m.group(1), "file": rel, "line": line_no(text, m.start())})
    return found


def parse_spawn_sites(source: Path):
    found = []
    pats = [r"tokio::spawn\s*\(", r"tokio::task::spawn\s*\(", r"std::thread::spawn\s*\("]
    for f in source.rglob("*.rs"):
        rel = f.relative_to(source).as_posix()
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in pats:
            for m in re.finditer(pat, text):
                ctx = text[max(0,m.start()-160): min(len(text),m.start()+220)].replace("\n"," ")
                found.append({"file":rel,"line":line_no(text,m.start()),"kind":pat.split("\\")[0],"context":re.sub(r"\s+"," ",ctx).strip()})
    return found


def parse_binaries(source: Path):
    out = []
    top = source / "src/main.rs"
    if top.exists(): out.append({"file":"src/main.rs","kind":"package-main"})
    for f in source.rglob("src/main.rs"):
        rel = f.relative_to(source).as_posix()
        if rel == "src/main.rs": continue
        out.append({"file":rel,"kind":"crate-main"})
    for f in source.rglob("src/bin/*.rs"):
        out.append({"file":f.relative_to(source).as_posix(),"kind":"bin-source"})
    return sorted(out,key=lambda x:x["file"])


def manifest_http_entries(manifest):
    out = set()
    for p in manifest["pages"]:
        if p["section"] != "HTTP / API": continue
        m = re.match(r"^(GET|POST|PUT|DELETE|PATCH)\s+([^\s]+)", p["entry"])
        if m:
            out.add(f"{m.group(1)} {normalize_path(m.group(2))}")
    return out


def is_non_runtime_source_route(r):
    path = r["file"]
    return any(x in path for x in ("/tests/", "crates/tests/", "examples/", "benches/")) or "#[cfg(test)]" in ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--manifest", default="docs/atlas-manifest.json")
    ap.add_argument("--json", default="docs/entrypoint-census.json")
    ap.add_argument("--report", default="docs/coverage-report.md")
    args = ap.parse_args()

    source = Path(args.source).resolve()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    source_sha = manifest["source_sha"]

    http_all = parse_http_routes(source)
    http = [r for r in http_all if not any(x in r["file"] for x in ("crates/tests/", "/tests/", "examples/", "benches/"))]
    dioxus = parse_dioxus_routes(source)
    spawns = parse_spawn_sites(source)
    binaries = parse_binaries(source)

    documented = manifest_http_entries(manifest)
    runtime_entries = {r["entry"] for r in http if r["method"] != "UNKNOWN"}
    covered = sorted(runtime_entries & documented)
    missing = sorted(runtime_entries - documented)
    documented_not_scanned = sorted(documented - runtime_entries)

    by_entry = defaultdict(list)
    for r in http:
        by_entry[r["entry"]].append(r)

    result = {
        "source_sha": source_sha,
        "manifest_page_count": manifest["page_count"],
        "counts": {
            "http_route_declarations": len(http),
            "http_unique_entries": len(runtime_entries),
            "http_documented_exact_matches": len(covered),
            "http_missing_exact_matches": len(missing),
            "dioxus_route_attributes": len(dioxus),
            "binary_source_entries": len(binaries),
            "spawn_sites": len(spawns),
        },
        "missing_http_entries": [
            {"entry": e, "declarations": by_entry[e]} for e in missing
        ],
        "documented_http_not_seen_as_direct_axum_route": documented_not_scanned,
        "http_routes": http,
        "dioxus_routes": dioxus,
        "binaries": binaries,
        "spawn_sites": spawns,
    }
    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "---",
        'title: "Coverage / Entry Point Census"',
        "slug: /coverage-report",
        "---",
        "",
        "# BurnCloud Entry Point Census",
        "",
        f"> 源码基线：`burncloud/burncloud@{source_sha}`。本页由 CI 直接扫描源码生成，不以人工枚举数量作为完整性证明。",
        "",
        "## 汇总",
        "",
        "| 项目 | 数量 |",
        "|---|---:|",
    ]
    for k,v in result["counts"].items():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## 源码存在但 Atlas 未精确匹配的 HTTP Route", ""]
    if not missing:
        lines.append("**0 个。** 当前扫描器识别到的直接 Axum Method + Path 声明均有 Atlas 页面精确匹配。")
    else:
        lines += ["| Entry | Source |", "|---|---|"]
        for e in missing:
            locs = ", ".join(f"`{x['file']}:{x['line']}`" for x in by_entry[e])
            lines.append(f"| `{e}` | {locs} |")
    lines += ["", "## Atlas 已记录但不是直接 `.route()` 精确声明的 HTTP Entry", "",
              "> 这里通常包含 Router fallback、兼容别名、LiveView 组合路由、特殊动态路径或人工语义页；需要人工确认，不直接判定为错误。", ""]
    for e in documented_not_scanned:
        lines.append(f"- `{e}`")
    lines += ["", "## Dioxus Route Attributes", "", "| Route | Source |", "|---|---|"]
    for r in dioxus:
        lines.append(f"| `{r['path']}` | `{r['file']}:{r['line']}` |")
    lines += ["", "## Binary / main.rs Candidates", "", "| Kind | Source |", "|---|---|"]
    for b in binaries:
        lines.append(f"| `{b['kind']}` | `{b['file']}` |")
    lines += ["", "## Async Spawn Sites", "", f"共扫描到 **{len(spawns)}** 个 `spawn` 站点。它们用于核对 Background Jobs / request-time async side effects 是否漏页。", "", "| Source | Line |", "|---|---:|"]
    for s in spawns:
        lines.append(f"| `{s['file']}` | {s['line']} |")
    Path(args.report).write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(json.dumps(result["counts"], ensure_ascii=False))
    if missing:
        print("MISSING_HTTP_ENTRIES:")
        for e in missing:
            print(" -", e)


if __name__ == "__main__":
    main()
