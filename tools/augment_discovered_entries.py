from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFEST = DOCS / "atlas-manifest.json"
SIDEBAR = ROOT / "site" / "sidebars.js"

DISCOVERED = [
    {
        "section": "CLI / Executables",
        "group": "Workspace Binaries",
        "title": "aria2-test",
        "entry": "aria2-test",
        "slug": "/cli/workspace-binaries/aria2-test",
        "docid": "cli/workspace-binaries/aria2-test",
        "source": "crates/download/crates/download-aria2/src/main.rs",
        "explanation": "独立 aria2 集成测试 binary：quick_start() 启动 Aria2Manager，创建 RPC client，读取全局统计和活跃任务，添加测试下载、查询任务状态，最后 shutdown manager。",
    }
]


def base_page(p, source_sha):
    return f'''---
title: "{p['title']}"
slug: {p['slug']}
hide_table_of_contents: true
---

# {p['title']}

**树路径：** `BurnCloud → {p['section']} → {p['group']} → {p['title']}`

> **中文解释：** {p['explanation']}
>
> **源码基线：** `burncloud/burncloud@{source_sha}`

## End-to-End Request Flow + ICFG

```text
START
│
├─ executable: {p['entry']}
│
▼
FILE: {p['source']}
│
├─ main()
├─ DECISION: startup succeeds?
│    ├─ NO → return Aria2Result error → END
│    └─ YES → execute binary workflow
│
▼
END
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `{p['source']}` |

**Execution classification: STATIC CONFIRMED** — 入口来自当前 workspace 的 `[[bin]]` / `src/main.rs` 定义。
'''


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {p["docid"] for p in data["pages"]}
    sidebar = SIDEBAR.read_text(encoding="utf-8")
    added = 0

    for p in DISCOVERED:
        if p["docid"] in existing:
            continue
        target = DOCS / (p["docid"] + ".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(base_page(p, data["source_sha"]), encoding="utf-8")
        data["pages"].append({k:p[k] for k in ("section","group","title","entry","slug","docid")})
        data["page_count"] += 1
        added += 1

        needle = '        {type:\'doc\', id:"cli/workspace-binaries/client-tray", label:"client-tray"},'
        row = f'        {{type:\'doc\', id:"{p["docid"]}", label:"{p["title"]}"}},'
        if row not in sidebar:
            if needle not in sidebar:
                raise RuntimeError("Workspace Binaries sidebar insertion point not found")
            sidebar = sidebar.replace(needle, needle + "\n" + row, 1)

    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    SIDEBAR.write_text(sidebar, encoding="utf-8")
    print(f"Added {added} census-discovered entrypoint pages; page_count={data['page_count']}")


if __name__ == "__main__":
    main()
