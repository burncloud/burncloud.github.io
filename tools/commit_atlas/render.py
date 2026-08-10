from __future__ import annotations

import json
import re
from pathlib import Path
from .common import *
from .analyze import *


def _yaml(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _path(s: str) -> str:
    return s.lower().replace("\\", "/")


def _plain_chain(steps: list[str]) -> str:
    out = []
    for idx, step in enumerate(steps):
        if idx:
            out += ["   │", "   ▼"]
        out.append(step)
    return "\n".join(out)


def plaintext_diff(unit: ChangeUnit) -> str:
    return (
        "```text\n"
        "[以前]\n"
        f"{_plain_chain(unit.before)}\n\n"
        "                 变成\n"
        "                  │\n"
        "                  ▼\n\n"
        "[现在]\n"
        f"{_plain_chain(unit.after)}\n"
        "```"
    )


def evidence_md(items, empty: str = "这个变化块没有可输出的历史行号证据。") -> str:
    if not items:
        return f"- **完整差异扫描：** {empty}"
    out = []
    names = {"BASE": "修改前", "AFTER": "修改后"}
    for side, sha, path, a, b in items:
        side = names.get(side, side)
        out.append(f"- **{side}:** [`{path}:L{a}-L{b}`]({historical_url(sha, path, a, b)})")
    return "\n".join(out)


def _unit_files(unit: ChangeUnit, limit: int = 8) -> list[str]:
    return list(dict.fromkeys(i.path for i in unit.items))[:limit]


def _one_line(units: list[ChangeUnit]) -> str:
    names = [u.title for u in units]
    if not names:
        return "这次提交有代码差异，但静态分析没有安全地归出一个明确的行为变化块。"
    if len(names) == 1:
        return f"这次主要改了一件事：**{names[0]}**。"
    if len(names) == 2:
        return f"这次主要改了两件事：**{names[0]}**，还有 **{names[1]}**。"
    return "这次主要改了这些事：" + "、".join(f"**{x}**" for x in names) + "。"


def _dimension_note(num: int, changed: bool, units: list[ChangeUnit], api_changed: bool, db_changed: bool, ext_changed: bool, tests: list[str]) -> str:
    if num == 1:
        return "代码文件和符号有变化。"
    if num == 2:
        return "有用户或管理员能直接感觉到的流程变化。" if changed else "没发现能安全映射到用户操作的变化。"
    if num == 3:
        return "程序实际运行时的步骤有变化。" if changed else "没发现生产运行链路变化。"
    if num == 4:
        return "有 if / match / loop / return 等控制逻辑变化。" if changed else "没发现明确的控制分支变化。"
    if num == 5:
        return "有数据库、页面状态、计数器或健康状态等写入变化。" if changed else "没发现明确的状态写入变化。"
    if num == 6:
        return "服务器公开接口的入口、状态码或返回契约有变化。" if api_changed else "没发现服务器公开 API 契约变化；客户端自己加请求头不自动算契约变化。"
    if num == 7:
        return "数据库迁移、表结构或持久化做法有变化。" if db_changed else "没发现数据库 / 持久化变化。"
    if num == 8:
        return "BurnCloud 调外部 Provider 的方式有变化。" if ext_changed else "没发现明确的外部 Provider 调用变化。"
    if num == 9:
        return "下面会把直接修改和可能受影响的地方分开列出来。"
    if num == 10:
        return f"这个提交同时改了 {len(tests)} 个测试文件。" if tests else "这个提交没有同步修改测试文件；不等于没有旧测试，只表示本次 diff 没加/改测试。"
    return ""


def _status(changed: bool) -> str:
    return "🟡 有变化" if changed else "⚪ 没发现变化"


def _flow_lines(units: list[ChangeUnit]) -> str:
    visible = [u for u in units if u.key not in {"database", "docs", "ci", "build", "tests", "general"}]
    if not visible:
        return "- 没发现可以安全说成『用户流程改变』的变化；不会为了凑图硬猜。"
    return "\n".join(f"- **{u.title}：** {u.flow}" for u in visible)


def _runtime_lines(units: list[ChangeUnit]) -> str:
    runtime = [u for u in units if u.key not in {"docs", "ci", "tests"}]
    if not runtime:
        return "- 这次主要是文档 / CI / 测试变化，没有发现线上运行步骤改变。"
    return "\n".join(f"- **{u.title}：** {u.plain}" for u in runtime)


def _control_summary(items: list[ChangeItem]) -> str:
    old = code_control_lines(items, "minus")
    new = code_control_lines(items, "plus")
    if not old and not new:
        return "**⚪ 没发现明确的 if / match / loop / return / spawn 控制语句变化。**"
    lines = ["这里**不把不同函数里的 if 强行串成一条假 ICFG**。只列真正改过的控制语句：", ""]
    if old:
        lines.append("**修改前删掉 / 改掉的控制点：**")
        lines += [f"- `{x}`" for x in old[:6]]
    if new:
        lines += ["", "**修改后新增 / 改过的控制点：**"]
        lines += [f"- `{x}`" for x in new[:6]]
    return "\n".join(lines)


def _state_summary(items: list[ChangeItem], units: list[ChangeUnit]) -> str:
    keys = {u.key for u in units}
    notes = []
    if "database" in keys:
        notes.append("数据库里的表、迁移或保存数据步骤发生变化。")
    if "auth" in keys and any(re.search(r"\.set\s*\(|token|jwt", i.text, re.I) for i in items):
        notes.append("登录 / Token 相关状态的处理发生变化。")
    if "ui" in keys and any(re.search(r"\.set\s*\(|modal_step|is_.*modal", i.text, re.I) for i in items):
        notes.append("页面里的弹窗开关、步骤等 UI 状态发生变化。")
    if "observability" in keys:
        notes.append("监控、日志、熔断或 Channel 健康状态的记录发生变化。")
    if not notes:
        return "- 没发现能安全概括的关键状态变化。"
    return "\n".join(f"- {x}" for x in notes)


def _api_summary(api_changed: bool, items: list[ChangeItem]) -> str:
    client_bearer = any(
        ("Authorization" in i.text or "Bearer" in i.text) and _path(i.path).startswith("crates/client/")
        for i in items
    )
    if not api_changed:
        extra = "\n\n> 注意：这次客户端虽然可能开始带 `Authorization: Bearer ...`，但这叫**客户端请求行为变化**，不能自动说成服务器公开 API 契约变了。" if client_bearer else ""
        return "**⚪ 没发现服务器公开 API 契约变化。**" + extra
    files = list(dict.fromkeys(i.path for i in items if _path(i.path).startswith(("crates/server/", "crates/router/"))))[:6]
    return "**🟡 检测到服务器 API 边界变化。**\n\n重点文件：\n" + "\n".join(f"- `{x}`" for x in files)


def _db_summary(units: list[ChangeUnit]) -> str:
    db = next((u for u in units if u.key == "database"), None)
    if not db:
        return "**⚪ 没发现数据库 / 持久化变化。**"
    return f"**🟡 有数据库变化。**\n\n{db.plain}\n\n涉及文件：\n" + "\n".join(f"- `{x}`" for x in _unit_files(db))


def _external_summary(changed: bool, units: list[ChangeUnit]) -> str:
    if not changed:
        return "**⚪ 没发现 BurnCloud 调外部 Provider 的方式发生明确变化。**"
    us = [u for u in units if u.key in {"provider", "streaming", "failover", "routing"}]
    return "**🟡 外部调用相关行为有变化。**\n\n" + "\n".join(f"- {u.plain}" for u in us)


def _impact_graph(units: list[ChangeUnit], blast) -> str:
    lines = ["```text", "这次 Commit"]
    for idx, u in enumerate(units):
        branch = "└─" if idx == len(units) - 1 else "├─"
        lines.append(f" {branch} {u.title}")
        lines.append(f" {'   ' if idx == len(units)-1 else '│  '}   └─ {u.flow}")
    if blast:
        lines += ["", "继续往代码里看（这里只是词法引用候选，不装成真实调用链）："]
        for depth, name, loc in blast[:8]:
            lines.append(f" - {depth}：{name} → {loc}")
    lines.append("```")
    return "\n".join(lines)


def _test_refs(repo: Path, target: str, symbols, limit=8):
    out = []
    for p, kind, name, ln in symbols[:12]:
        if len(name) < 4:
            continue
        g = run(repo, "grep", "-n", "-F", name, target, "--", "*test*.rs", "tests/**/*.rs", check=False)
        if g.strip():
            out.append((name, g.splitlines()[0]))
        if len(out) >= limit:
            break
    return out


def render(repo: Path, out: Path, pr, pos: int):
    target = pr["merge_commit_sha"]
    parents = run(repo, "show", "-s", "--format=%P", target).strip().split()
    if not parents:
        raise RuntimeError(f"{target} has no parent")
    base = parents[0]
    diff = run(repo, "diff", base, target, "--find-renames", "--unified=0")
    files = parse_patch(diff)
    paths = [f.path for f in files]
    symbols = changed_symbols(repo, files, base, target)
    funcs = [x for x in symbols if x[1] == "function"]
    tests_changed = [p for p in paths if is_test(p)]
    items = collect_items(files)
    units = build_units(files, pr, limit=5)
    dims = dimension_model(files, units, tests_changed)
    score, risk, drivers = risk_model(files, units, tests_changed, dims)
    api_changed = dims[6][1]
    db_changed = dims[7][1]
    ext_changed = dims[8][1]
    blast = blast_candidates(repo, target, symbols)
    test_refs = _test_refs(repo, target, symbols)

    name_status = run(repo, "diff", "--name-status", base, target, "--find-renames").splitlines()
    changed_files = []
    for row in name_status:
        parts = row.split("\t")
        changed_files.append((parts[0], parts[-1]))

    slug = f"{pr['merged_at'][:10]}-pr-{pr['number']}-{target[:8]}"
    title = pr.get("title") or f"PR #{pr['number']}"
    body = (pr.get("body") or "").strip()
    one = _one_line(units)

    unit_sections = []
    for idx, u in enumerate(units, 1):
        paths_md = "\n".join(f"- `{p}`" for p in _unit_files(u)) or "- 没有文件"
        ev = evidence_md(unit_evidence(u, base, target))
        unit_sections.append(f'''### 变化 {idx}：{u.title}

**大白话：** {u.plain}

**谁会感觉到：** {u.flow}

#### 以前 → 现在

{plaintext_diff(u)}

#### 这块主要改了哪些文件

{paths_md}

#### 源码证据

{ev}
''')

    dashboard = ["| 维度 | 结果 | 大白话 |", "|---|---|---|"]
    for n in range(1, 11):
        label, changed = dims[n]
        if n == 10 and not tests_changed:
            st = "⚠️ 本提交没改测试"
        else:
            st = _status(changed)
        dashboard.append(f"| {n}. {label} | {st} | {_dimension_note(n, changed, units, api_changed, db_changed, ext_changed, tests_changed)} |")

    unit_names = "、".join(u.title for u in units) or "未安全归类"
    risk_drivers = "\n".join(f"- {name}：`+{pts}`" for name, pts in drivers) or "- 没命中高风险规则。"
    changed_files_short = "\n".join(
        f"- {'🟢 新增' if s.startswith('A') else '🔴 删除' if s.startswith('D') else '🟡 修改'} `{p}`"
        for s, p in changed_files[:20]
    ) or "- 没有文件差异。"
    symbol_short = "\n".join(f"- `{name}` — `{path}:L{ln}`" for path, kind, name, ln in symbols[:12]) or "- 没有安全解析出的 Rust 符号；不会硬猜。"

    control = _control_summary(items)
    state = _state_summary(items, units)
    api = _api_summary(api_changed, items)
    db = _db_summary(units)
    ext = _external_summary(ext_changed, units)
    impact = _impact_graph(units, blast)

    if tests_changed:
        tests_md = "**本提交同步修改了测试：**\n" + "\n".join(f"- `{p}`" for p in tests_changed[:12])
    else:
        tests_md = "**⚠️ 本提交没有同步修改测试文件。** 这不等于项目没有旧测试，只表示这次提交本身没有加 / 改测试。"
    if test_refs:
        tests_md += "\n\n**名字匹配到的可能相关旧测试（只是候选，不冒充已覆盖）：**\n" + "\n".join(f"- `{name}` → `{loc}`" for name, loc in test_refs)

    all_ev = evidence(files, base, target, limit=10)
    all_evidence = evidence_md(all_ev, "完整 diff 没有可输出的行号证据。")

    doc = f'''---
title: "PR #{pr['number']} · {_yaml(title)}"
slug: /commits/{slug}/
sidebar_position: {pos}
doc_type: commit-change-atlas-v2
truth: source-diff-derived
language: zh-CN
diagram_style: plaintext
repository: {REPO}
pr_number: {pr['number']}
base_commit: {base}
target_commit: {target}
risk: {risk}
merged_at: {pr['merged_at']}
---

# PR #{pr['number']}：这次到底改了什么？

## 一句话先看懂

{one}

**风险：{risk}（{score} 分）** · 改了 **{len(paths)}** 个文件 · 先看 **{len(units)}** 个真正的变化块

> **作者写的目的（AUTHOR-STATED INTENT）：** {title}

{('> **作者补充说明（原文）：** ' + body.replace(chr(10), ' ')) if body else '> 作者没有写额外说明；下面只按源码差异说话。'}

**完整源码差异：** [BASE `{base[:12]}` → TARGET `{target[:12]}`]({compare_url(base, target)})

---

## 这次主要改了什么

不要先看 {len(symbols)} 个符号。先把这次提交当成 **{len(units)} 件独立的事情** 看：**{unit_names}**。

{chr(10).join(unit_sections)}

---

## 10 个修改维度

这 10 个维度是**检查清单**，不是阅读顺序。上面的“变化块”才是人真正应该先看的。

{chr(10).join(dashboard)}

---

## 1. 修改范围

**改了什么：** {len(paths)} 个文件，静态解析到 {len(symbols)} 个 Rust 符号，其中 {len(funcs)} 个函数。

**先看这些变化块：** {unit_names}。

### 主要文件（最多 20 个）

{changed_files_short}

### 主要代码入口（最多 12 个）

{symbol_short}

---

## 2. 用户流程

{_flow_lines(units)}

> 只有能从这次 diff 安全对应到用户 / 管理员操作的变化才写在这里。数据库迁移、CI、文档不会被硬说成“用户流程”。

---

## 3. 运行过程

{_runtime_lines(units)}

**真正的 BEFORE → AFTER 已经放在每个“变化块”的 plaintext 图里。不同功能不会被强行接成一条假 E2E。**

---

## 4. 控制流程

{control}

---

## 5. 状态变化

{state}

---

## 6. API 契约

{api}

---

## 7. 数据库 / 持久化

{db}

---

## 8. 外部依赖

{ext}

---

## 9. 影响范围

{impact}

> “可能受影响（词法引用）”只说明代码里找到了同名引用，**不等于已经证明是一条真实调用链**。

---

## 10. 测试与证据

{tests_md}

### 本次提交的历史源码证据

{all_evidence}

---

## 风险判断

**总分：{score} → {risk}风险**

{risk_drivers}

这个分数来自固定规则，不是 AI 凭感觉打分。

## 程序员 Review 清单

- [ ] 我能用一句话说清这次改了哪几件事
- [ ] 每个变化块的“以前 → 现在”符合真实源码
- [ ] 没把两个不相关的功能画成一条假流程
- [ ] 登录 / 权限变化已经单独确认
- [ ] 数据库迁移变化已经单独确认
- [ ] API 契约和“客户端请求行为”没有混为一谈
- [ ] 外部 Provider 调用变化已经确认
- [ ] 影响范围里的“可能”没有被当成“确定”
- [ ] 测试是否覆盖关键变化已经人工确认
- [ ] 所有重要结论都能点回 BASE / TARGET 历史源码

## 直接看源码

- [完整 BASE → TARGET Diff]({compare_url(base, target)})
- [原 Pull Request #{pr['number']}]({pr['html_url']})
'''

    out.mkdir(parents=True, exist_ok=True)
    md = out / f"{slug}.md"
    md.write_text(doc, encoding="utf-8")

    record = {
        "version": 2,
        "pr_number": pr["number"],
        "title": title,
        "merged_at": pr["merged_at"],
        "base": base,
        "target": target,
        "risk": risk,
        "risk_score": score,
        "files_changed": len(paths),
        "changed_symbols": len(symbols),
        "changed_functions": len(funcs),
        "summary": one.replace("**", ""),
        "semantic_units": [
            {"key": u.key, "title": u.title, "plain": u.plain, "flow": u.flow, "files": _unit_files(u)}
            for u in units
        ],
        "dimensions": {str(n): {"name": dims[n][0], "changed": dims[n][1]} for n in range(1, 11)},
        "doc": md.name,
    }
    (out / f"{slug}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def write_index(root: Path, records):
    lines = [
        "---",
        'title: "BurnCloud 最近 30 次更新"',
        "slug: /",
        "sidebar_position: 1",
        "doc_type: commit-change-index-v2",
        "---",
        "",
        "# BurnCloud 最近 30 次更新",
        "",
        "这里不用一上来读几千行 Diff。每次更新先回答三个问题：**改了哪几件事、以前怎么跑、现在怎么跑。**",
        "",
        "每篇文档都用中文大白话和 plaintext 网络图。10 个修改维度放在后面当检查清单。",
        "",
        "## 最近 30 个已合并更新",
        "",
        "| # | 日期 | PR | 一句话 | 风险 | 文件 |",
        "|---:|---|---|---|---|---:|",
    ]
    for idx, r in enumerate(records, 1):
        slug = Path(r["doc"]).stem
        summary = r["summary"].replace("|", "¦")
        lines.append(
            f"| {idx} | {r['merged_at'][:10]} | [#{r['pr_number']}]({WEB}/pull/{r['pr_number']}) | "
            f"[{summary}](./commits/{slug}.md) | **{r['risk']}** | {r['files_changed']} |"
        )
    lines += [
        "",
        "## 每篇都会检查的 10 个维度",
        "",
        "1. 修改范围",
        "2. 用户流程",
        "3. 运行过程",
        "4. 控制流程",
        "5. 状态变化",
        "6. API 契约",
        "7. 数据库 / 持久化",
        "8. 外部依赖",
        "9. 影响范围",
        "10. 测试与证据",
        "",
        "> 规则：源码差异优先，证据优先，不知道就写不知道，不为了画图把不相关代码连在一起。",
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (root / "commit-index.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "commits" / "_category_.json").write_text(
        json.dumps({"label": "最近 30 次更新", "position": 2, "collapsed": False}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
