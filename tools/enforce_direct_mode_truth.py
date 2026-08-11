from pathlib import Path
import argparse
import json
import re

import enrich_execution_truth_v4 as v4

DIRECT = {"burncloud", "burncloud server", "burncloud router", "burncloud client"}
RESULT_RE = re.compile(r"(## 返回结果示例\n\n).*?(?=\n## 穿过的源码文件（详细）)", re.S)


def replace_result(text: str, entry: str) -> str:
    if entry in {"burncloud server", "burncloud router"}:
        note = (
            "> 以下采用源码真实 tracing 文案；示例按未设置 HOST/PORT 时的默认值 "
            "`127.0.0.1:3000` 展示。时间戳、日志级别和 target 由 tracing formatter 决定。\n\n"
        )
        body = """```text
Unified Gateway listening on 127.0.0.1:3000
- Dashboard: http://127.0.0.1:3000/
- LLM API:   http://127.0.0.1:3000/v1/...

# 随后 axum::serve 持续运行，命令不会立即返回到 Shell。
```\n\n"""
    elif entry == "burncloud":
        note = "> 无参数启动存在平台分支；下面分别给出源码可确认的终态/输出语义。\n\n"
        body = """```text
# 非 Windows
Starting BurnCloud Server with LiveView (Headless Mode)...
Unified Gateway listening on 127.0.0.1:3000
- Dashboard: http://127.0.0.1:3000/
- LLM API:   http://127.0.0.1:3000/v1/...

# Windows
background_server_thread=running (enable_liveview=false)
desktop_gui_event_loop=running
system_tray_thread=running
```\n\n"""
    elif entry == "burncloud client":
        note = "> `client` 是平台分支入口：Windows 进入 Dioxus Desktop 事件循环；非 Windows 的两行提示是源码真实 stdout。\n\n"
        body = """```text
# Windows
BurnCloud desktop window + tray enter the long-running GUI event loop.

# 非 Windows（源码真实 stdout）
Desktop GUI is only available on Windows.
On Linux, use 'burncloud server' to start the web dashboard.
```\n\n"""
    else:
        return text

    m = RESULT_RE.search(text)
    if not m:
        raise RuntimeError(f"result section not found: {entry}")
    return text[:m.start()] + m.group(1) + note + body + text[m.end():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--manifest", default="docs/atlas-manifest.json")
    args = ap.parse_args()

    src = Path(args.source).resolve()
    mp = Path(args.manifest)
    docs = mp.parent
    manifest = json.loads(mp.read_text(encoding="utf-8"))

    fixed = 0
    for p in manifest["pages"]:
        if p["entry"] not in DIRECT:
            continue
        path = docs / (p["docid"] + ".md")
        text = path.read_text(encoding="utf-8")

        # Re-apply the manually audited branch-specific flow AFTER generic static
        # call expansion. This intentionally removes calls from non-selected
        # match branches (for example the generic Clap CLI path on `server`).
        text, applied = v4.special_direct(p, src, text)
        if not applied:
            raise RuntimeError(f"direct-mode rewrite not applied: {p['entry']}")

        # Source-path strings in the graph mean traversed source only. Do not put
        # a false-path filename in a negative explanation.
        text = text.replace(
            "│    └─ 此路径不会进入 src/cli/commands.rs",
            "│    └─ 此 direct branch 不进入 Clap CLI dispatch",
        )

        text = replace_result(text, p["entry"])

        text = text.replace(
            "**Execution classification: STATIC CONFIRMED**",
            "**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE**",
        )
        text = text.replace(
            "**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION**",
            "**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE**",
        )
        path.write_text(text, encoding="utf-8")
        fixed += 1

    if fixed != 4:
        raise RuntimeError(f"expected 4 direct-mode pages, fixed {fixed}")
    print(f"Restored branch-sensitive direct-mode truth on {fixed} pages")


if __name__ == "__main__":
    main()
