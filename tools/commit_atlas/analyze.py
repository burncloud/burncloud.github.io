from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from .common import *

# V2 rule: classify each changed hunk first. Never map the whole commit to a runtime flow
# merely because one keyword appeared somewhere in the diff.

CONTROL_LINE = re.compile(
    r"^\s*(?:else\s+)?if\b|^\s*match\b|^\s*for\s+\w+\s+in\b|^\s*while\b|"
    r"^\s*loop\b|^\s*(?:return|continue|break)\b|\b(?:tokio::)?spawn\s*\(", re.I
)
STATE_LINE = re.compile(
    r"\.set\s*\(|\.write\s*\(|\.insert\s*\(|\.remove\s*\(|\.evict\s*\(|"
    r"\.reset\s*\(|record_[a-z_]+\s*\(|fetch_(?:add|sub)\s*\(|"
    r"\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b", re.I
)
PUBLIC_API_LINE = re.compile(
    r"\.route\s*\(|StatusCode::|Json\s*\(|IntoResponse|Content-Type|CONTENT_TYPE|"
    r"Retry-After|response\s+header|/v1/|/api/", re.I
)
OUTBOUND_LINE = re.compile(
    r"reqwest|\.send\s*\(\)\s*\.await|base_url|upstream|adaptor|provider|timeout\s*\(", re.I
)

@dataclass
class ChangeItem:
    path: str
    old_path: str
    new_path: str
    hunk: Hunk
    plus: list[str]
    minus: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.plus + self.minus)

    @property
    def size(self) -> int:
        return max(1, len(self.plus) + len(self.minus))

@dataclass
class ChangeUnit:
    key: str
    title: str
    plain: str
    flow: str
    before: list[str]
    after: list[str]
    items: list[ChangeItem] = field(default_factory=list)
    score: int = 0
    truth: str = "源码差异确认"

DOMAIN = {
    "auth": ("登录和鉴权", "用户登录 / 访问受保护的 Console 接口", 55),
    "database": ("数据库升级和保存数据", "程序启动 / 数据库升级 / 保存数据", 50),
    "streaming": ("流式返回", "用户发起流式模型请求", 50),
    "failover": ("上游失败后换下一个渠道", "上游失败后的重试 / Failover", 48),
    "routing": ("模型请求选渠道", "模型请求选择 Channel", 44),
    "provider": ("调用上游模型服务", "BurnCloud 调用上游 Provider", 44),
    "observability": ("监控、日志和熔断状态", "管理员查看监控 / 系统记录运行状态", 38),
    "api": ("后台接口", "客户端或外部程序调用 BurnCloud API", 42),
    "console": ("Console 调后台接口", "管理员在 Console 页面操作", 34),
    "ui": ("弹窗、按钮和页面界面", "管理员使用 Console 页面", 30),
    "ci": ("代码检查和自动化", "开发者提交代码后运行 CI", 24),
    "docs": ("开发文档", "程序员 / AI Agent 阅读工程文档", 20),
    "tests": ("自动测试", "开发者运行测试", 18),
    "build": ("编译、依赖和启动配置", "开发者编译或启动 BurnCloud", 18),
    "general": ("其他代码整理", "代码内部行为；需要按源码证据继续确认入口", 10),
}

AUTHOR_HINTS = {
    "auth": re.compile(r"jwt|auth|login|token|secret|鉴权|认证", re.I),
    "database": re.compile(r"sqlite|postgres|database|migration|schema|数据库|迁移", re.I),
    "streaming": re.compile(r"stream|sse|first chunk|流式", re.I),
    "failover": re.compile(r"retry|failover|fallback|429|熔断|重试", re.I),
    "routing": re.compile(r"routing|scheduler|channel selection|route|路由|渠道选择", re.I),
    "provider": re.compile(r"provider|upstream|openai|anthropic|gemini|zai|上游", re.I),
    "observability": re.compile(r"monitor|log|circuit|health|metrics|监控|日志|熔断", re.I),
    "ui": re.compile(r"modal|sidebar|button|ui|css|desktop|layout|弹窗|界面", re.I),
    "ci": re.compile(r"workflow|ci|gate|lint|check", re.I),
    "docs": re.compile(r"docs|documentation|readme|文档", re.I),
}


def _low(path: str) -> str:
    return path.lower().replace("\\", "/")


def _looks_ui(path: str, text: str) -> bool:
    p = _low(path)
    return (
        "/client" in p
        and bool(re.search(r"components?|styles?\.rs|\.css$|sidebar|modal|button|layout|page|dashboard|models\.rs|connect/src", p))
    ) or bool(re.search(r"\bBCModal\b|\bBCButton\b|rsx!|class:\s*[\"']|aria_label|sidebar", text, re.I))


def classify_hunk(path: str, text: str) -> str:
    p = _low(path)
    t = text

    if is_test(path):
        return "tests"
    if p.startswith("docs/") or p.endswith("readme.md") or "/docs/" in p:
        return "docs"
    if p.startswith(".github/") or "workflow" in p or "check-ui" in p or "check_router" in p or "check-router" in p:
        return "ci"
    if p.endswith("cargo.toml") or p.endswith("cargo.lock") or p.endswith("package.json"):
        return "build"

    # Persistence classification is path-first. This prevents CSS 'select-none' / 'user-select'
    # from ever being interpreted as SQL SELECT.
    if (
        p.startswith("crates/database/")
        or "/database/" in p
        or "/migrations/" in p
        or p.endswith(".sql")
        or "migration" in p
    ):
        return "database"

    if re.search(r"DEFAULT_JWT_SECRET|Authorization|Bearer|auth_http|auth_service|verify_jwt|encode_jwt|decode_jwt|Claims\b|login|password", t, re.I):
        return "auth"
    if any(x in p for x in ["auth_service", "auth_http", "/auth/", "jwt", "login"]):
        return "auth"

    if p.startswith("crates/router/") or "/router/" in p:
        if re.search(r"peek_first_chunk|bytes_stream|SSE|streaming|stream_peek|UnifiedTokenCounter", t, re.I):
            return "streaming"
        if re.search(r"failover|retry|429|TOO_MANY_REQUESTS|record_upstream_failure|next candidate|continue|circuit", t, re.I):
            return "failover"
        if re.search(r"reqwest|upstream|provider|adaptor|base_url|ChannelType", t, re.I):
            return "provider"
        return "routing"

    if re.search(r"CircuitBreaker|ChannelHealth|HealthProbe|SystemMonitor|Prometheus|router_request_logs|record_upstream_(?:success|failure)|EmptyResponseCounter", t, re.I) or any(x in p for x in ["monitor", "metrics", "health", "request_log", "circuit"]):
        return "observability"

    if re.search(r"reqwest|DynamicAdaptor|ProviderType|ChannelType|upstream|base_url", t, re.I) and not _looks_ui(path, t):
        return "provider"

    if _looks_ui(path, t):
        return "ui"

    if p.startswith("crates/server/") or "/server/" in p:
        return "api"
    if p.startswith("crates/client/") or "/client-" in p:
        return "console"
    return "general"


def changed_symbols(repo: Path, files, base: str, target: str):
    ans = set()
    for f in files:
        if not f.path.endswith(".rs"):
            continue
        for sha, p, newside in [(target, f.newp, True), (base, f.oldp, False)]:
            lines = show_lines(repo, sha, p)
            for h in f.hunks:
                start = h.new if newside else h.old
                count = h.newn if newside else h.oldn
                if count <= 0:
                    continue
                for ln in range(start, start + count):
                    for k in range(min(ln - 1, len(lines) - 1), max(-1, ln - 80), -1):
                        m = DECL.match(lines[k])
                        if m:
                            kind = "function" if m.group(1) else m.group(3)
                            name = m.group(2) or m.group(4)
                            ans.add((p, kind, name, k + 1))
                            break
    return sorted(ans)


def collect_items(files) -> list[ChangeItem]:
    out = []
    for f in files:
        for h in f.hunks:
            out.append(ChangeItem(f.path, f.oldp, f.newp, h, h.plus[:], h.minus[:]))
    return out


def _text(items: list[ChangeItem], side: str = "all") -> str:
    lines = []
    for i in items:
        if side in ("all", "plus"):
            lines.extend(i.plus)
        if side in ("all", "minus"):
            lines.extend(i.minus)
    return "\n".join(lines)


def _author_text(pr) -> str:
    return f"{pr.get('title','')}\n{pr.get('body') or ''}"


def _describe_auth(items, pr):
    add = _text(items, "plus")
    body = _author_text(pr)
    shared = "DEFAULT_JWT_SECRET" in add
    bearer = bool(re.search(r"Authorization|Bearer|auth_http", add, re.I))
    if shared and bearer:
        plain = "登录后的 Token 处理被统一了。现在客户端有 Token 时会带上 Bearer 头，签发和检查 JWT 也尽量走同一套密钥。"
        before = ["用户登录", "拿到 JWT", "后面的 Console 请求按旧方式带 Token / 验 Token", "这些规则分散，容易对不上"]
        after = ["用户登录", "用同一个 DEFAULT_JWT_SECRET 处理 JWT", "客户端带 Authorization: Bearer ...", "服务器按同一套规则检查", "受保护的 Console 接口继续处理请求"]
    else:
        plain = "这次改了登录、Token 或权限检查。重点是让『拿到身份』和『后面检查身份』的代码更一致。"
        before = ["用户登录或发请求", "走旧的 Token / 权限处理"]
        after = ["用户登录或发请求", "走这次修改后的 Token / 权限处理", "再进入受保护功能"]
    if "login sessions work" in body.lower():
        plain += " 这是作者在 PR 里明确写出的修复目标。"
    return plain, before, after


def _describe_database(items, pr):
    add = _text(items, "plus")
    paths = "\n".join(i.path for i in items)
    sqlite17 = "sqlite_0017" in paths or "0017_fix_bool" in paths
    if sqlite17:
        plain = "SQLite 的第 0017 次数据库升级被重做了，目的是让旧数据库升级时更稳，不要因为旧表结构不同就直接出问题。"
        before = ["程序打开旧 SQLite 数据库", "按原来的 0017 SQL 升级", "旧表结构不完全一样时容易出问题"]
        after = ["程序打开旧 SQLite 数据库", "运行新的 0017 迁移逻辑", "先检查 / 搬运旧表数据", "把数据库升级到现在需要的结构"]
    elif re.search(r"CREATE TABLE|ALTER TABLE|migration", add, re.I):
        plain = "这次改了数据库结构或升级步骤。程序启动或升级数据库时，会按新的迁移规则处理。"
        before = ["读取旧数据库", "按旧结构 / 旧迁移继续运行"]
        after = ["读取旧数据库", "执行新的数据库迁移", "按新结构继续运行"]
    else:
        plain = "这次改了数据库的读写方式。表不一定变了，但保存或查询数据的方法变了。"
        before = ["业务代码", "按旧 SQL / 旧保存方式读写数据"]
        after = ["业务代码", "按新的 SQL / 保存方式读写数据"]
    return plain, before, after


def _describe_ui(items, pr):
    add, old = _text(items, "plus"), _text(items, "minus")
    modal = "BCModal" in add or bool(re.search(r"modal", add + old, re.I))
    sidebar = bool(re.search(r"sidebar|title.?bar", add + old, re.I))
    if modal:
        plain = "Console 的弹窗和页面交互被整理了。以前有些页面自己写一套弹窗，现在更多地方统一用 BCModal，关闭或保存时也把页面状态收干净。"
        before = ["管理员打开 Console 页面", "页面自己维护弹窗和按钮", "关闭 / 保存时各页面自己处理状态"]
        after = ["管理员打开 Console 页面", "统一使用 BCModal / 公共按钮组件", "关闭或保存", "把弹窗步骤和页面状态复位"]
    elif sidebar:
        plain = "Console 的侧边栏、标题栏或布局被调整了。主要影响『页面怎么显示、按钮怎么点』，不是模型请求主链路。"
        before = ["管理员打开 Console", "看到旧的页面布局"]
        after = ["管理员打开 Console", "看到新的侧边栏 / 标题栏 / 布局"]
    else:
        plain = "这次主要整理 Console 界面。用户看到的按钮、样式或页面交互发生了变化。"
        before = ["管理员打开页面", "使用旧的按钮 / 样式 / 交互"]
        after = ["管理员打开页面", "使用这次更新后的按钮 / 样式 / 交互"]
    return plain, before, after


def _describe_streaming(items, pr):
    add = _text(items, "plus")
    if re.search(r"peek_first_chunk|first chunk|SSE", add, re.I):
        plain = "流式回复不会一拿到连接就马上交给用户了。现在会先看第一块数据；如果第一块已经是上游错误，就还有机会换一个渠道。"
        before = ["用户发起流式请求", "上游返回一个流", "马上把流交给客户端", "第一块就是错误时也很难再换渠道"]
        after = ["用户发起流式请求", "上游返回一个流", "先看第一块数据", "第一块正常 → 继续流给用户", "第一块报错 → 进入失败 / 重试处理"]
    else:
        plain = "这次改了流式响应的处理顺序。重点要看数据什么时候开始交给客户端，以及出错后还能不能重试。"
        before = ["流式请求", "按旧的流处理顺序返回"]
        after = ["流式请求", "按新的流处理顺序检查并返回"]
    return plain, before, after


def _describe_failover(items, pr):
    add = _text(items, "plus")
    plain = "上游出错以后，BurnCloud 决定『直接报错』还是『换下一个渠道再试』的规则变了。"
    before = ["请求发给当前 Channel", "上游失败", "按旧规则决定是否结束"]
    after = ["请求发给当前 Channel", "上游失败", "记录失败状态", "符合条件 → 换下一个候选 Channel", "不符合条件 → 返回错误"]
    if re.search(r"429|TOO_MANY_REQUESTS", add, re.I):
        plain += " 这次代码里还明确碰到了 429 限流处理。"
    return plain, before, after


def _describe_routing(items, pr):
    return (
        "模型请求挑选 Channel 的规则变了。要关心的是：哪些渠道能进候选、怎么排序、最后先试谁。",
        ["模型请求进来", "按旧规则找候选 Channel", "选出要先尝试的 Channel"],
        ["模型请求进来", "按新规则过滤 / 排序候选 Channel", "选出新的尝试顺序"],
    )


def _describe_provider(items, pr):
    return (
        "BurnCloud 调上游模型服务的代码变了。可能涉及请求地址、请求头、协议转换或返回结果处理。",
        ["BurnCloud 准备上游请求", "按旧方式调用 Provider", "读取 Provider 返回"],
        ["BurnCloud 准备上游请求", "按这次修改后的方式调用 Provider", "读取并处理 Provider 返回"],
    )


def _describe_observability(items, pr):
    return (
        "系统记录健康状态、日志、监控或熔断信息的办法变了。它主要帮助系统知道『哪个渠道好不好用』以及管理员排查问题。",
        ["请求运行", "按旧方式记录日志 / 健康状态"],
        ["请求运行", "按新方式记录日志 / 健康状态", "监控或熔断逻辑读取这些状态"],
    )


def _describe_api(items, pr):
    return (
        "后台接口代码变了。普通程序员要重点确认：入口、返回格式、状态码或鉴权有没有一起变化。",
        ["客户端调用接口", "旧的 route / handler", "返回旧结果"],
        ["客户端调用接口", "修改后的 route / handler", "返回修改后的结果"],
    )


def _describe_console(items, pr):
    return (
        "Console 页面调用后台接口的代码变了。也就是管理员点一个操作后，前端怎么请求后台发生了变化。",
        ["管理员在 Console 点操作", "客户端按旧方式调用后台"],
        ["管理员在 Console 点操作", "客户端按新方式调用后台", "页面拿到结果后刷新 / 提示"],
    )


def _describe_docs(items, pr):
    return (
        "这次主要整理开发文档。它会影响程序员和 AI Agent 怎么理解项目，但不会因为文档本身就改变线上请求怎么跑。",
        ["程序员 / AI Agent", "阅读旧文档", "按旧说明理解代码"],
        ["程序员 / AI Agent", "阅读新文档", "按新的工程事实和规则找代码"],
    )


def _describe_ci(items, pr):
    return (
        "这次改的是自动检查和发布流程。用户平时调用 BurnCloud 的运行链路通常不变，但开发者提交代码后的检查方法变了。",
        ["开发者提交代码", "跑旧的 CI / 检查脚本"],
        ["开发者提交代码", "跑新的 CI / 检查脚本", "通过后才允许继续发布"]
    )


def _describe_tests(items, pr):
    return (
        "这次主要改自动测试。它是在告诉我们『以后哪些行为必须继续成立』。",
        ["运行旧测试", "检查旧的行为范围"],
        ["运行新测试", "检查这次补充 / 调整后的行为范围"],
    )


def _describe_build(items, pr):
    return (
        "这次改了依赖、编译或启动配置。业务代码不一定变，但『项目怎么装、怎么编、怎么启动』变了。",
        ["开发者准备项目", "使用旧依赖 / 旧配置编译或启动"],
        ["开发者准备项目", "使用新依赖 / 新配置编译或启动"],
    )


def _describe_general(items, pr):
    return (
        "这部分代码有变化，但仅靠静态差异还不能安全地说它属于哪条用户流程，所以这里不硬猜。",
        ["旧代码路径", "按 BASE 版本运行"],
        ["同一代码路径", "按 TARGET 版本运行", "具体入口请看下面的源码证据"],
    )

DESCRIBERS = {
    "auth": _describe_auth,
    "database": _describe_database,
    "ui": _describe_ui,
    "streaming": _describe_streaming,
    "failover": _describe_failover,
    "routing": _describe_routing,
    "provider": _describe_provider,
    "observability": _describe_observability,
    "api": _describe_api,
    "console": _describe_console,
    "docs": _describe_docs,
    "ci": _describe_ci,
    "tests": _describe_tests,
    "build": _describe_build,
    "general": _describe_general,
}


def build_units(files, pr, limit: int = 5) -> list[ChangeUnit]:
    buckets: dict[str, list[ChangeItem]] = {}
    for item in collect_items(files):
        key = classify_hunk(item.path, item.text)
        buckets.setdefault(key, []).append(item)

    # Tests are a coverage dimension. Only promote them to a top-level semantic change when the
    # commit has no non-test change at all.
    non_test = [k for k in buckets if k != "tests"]
    candidates = non_test or list(buckets)
    author = _author_text(pr)
    ranked = []
    for key in candidates:
        items = buckets[key]
        _, _, bonus = DOMAIN[key]
        changed = sum(i.size for i in items)
        author_bonus = 30 if key in AUTHOR_HINTS and AUTHOR_HINTS[key].search(author) else 0
        critical_bonus = 25 if key in {"auth", "database", "streaming", "failover"} else 0
        ranked.append((changed + bonus + author_bonus + critical_bonus, key, items))
    ranked.sort(reverse=True)

    # Keep at most five independent stories. Critical domains with evidence are never dropped
    # simply because a huge UI formatting diff has more lines.
    chosen = ranked[:limit]
    critical_present = [x for x in ranked if x[1] in {"auth", "database", "streaming", "failover"}]
    for item in critical_present:
        if item not in chosen:
            chosen[-1] = item
    chosen = sorted({x[1]: x for x in chosen}.values(), reverse=True)[:limit]

    units = []
    for score, key, items in chosen:
        title, flow, _ = DOMAIN[key]
        plain, before, after = DESCRIBERS[key](items, pr)
        units.append(ChangeUnit(key, title, plain, flow, before, after, items, score))
    return units


def code_control_lines(items: list[ChangeItem], side: str) -> list[str]:
    out = []
    for i in items:
        if not i.path.endswith(".rs") or is_test(i.path):
            continue
        lines = i.plus if side == "plus" else i.minus
        for raw in lines:
            s = raw.strip()
            if not s or s.startswith(("//", "/*", "*", "///")):
                continue
            if CONTROL_LINE.search(s):
                out.append(compact(s, 90))
    return list(dict.fromkeys(out))[:10]


def state_lines(items: list[ChangeItem], side: str) -> list[str]:
    out = []
    for i in items:
        if is_test(i.path):
            continue
        lines = i.plus if side == "plus" else i.minus
        for raw in lines:
            s = raw.strip()
            if s.startswith(("//", "/*", "*", "///")):
                continue
            if STATE_LINE.search(s):
                out.append(compact(s, 95))
    return list(dict.fromkeys(out))[:10]


def public_api_changed(items: list[ChangeItem]) -> bool:
    for i in items:
        p = _low(i.path)
        # A client adding Authorization is request behavior, not automatically a public server contract.
        if not (p.startswith("crates/server/") or p.startswith("crates/router/") or "/server/" in p):
            continue
        if PUBLIC_API_LINE.search(i.text):
            return True
    return False


def external_changed(items: list[ChangeItem]) -> bool:
    for i in items:
        p = _low(i.path)
        if p.startswith("crates/router/") or "provider" in p or "adaptor" in p:
            if OUTBOUND_LINE.search(i.text):
                return True
    return False


def database_changed(items: list[ChangeItem]) -> bool:
    return any(classify_hunk(i.path, i.text) == "database" for i in items)


def dimension_model(files, units: list[ChangeUnit], tests_changed: list[str]):
    all_items = collect_items(files)
    keys = {u.key for u in units}
    runtime_keys = {"auth", "database", "streaming", "failover", "routing", "provider", "observability", "api", "console", "ui", "general"}
    control = bool(code_control_lines(all_items, "plus") or code_control_lines(all_items, "minus"))
    state = bool(state_lines(all_items, "plus") or state_lines(all_items, "minus"))
    api = public_api_changed(all_items)
    db = database_changed(all_items)
    ext = external_changed(all_items)
    runtime = bool(keys & runtime_keys)
    user = bool(keys & {"auth", "streaming", "failover", "routing", "provider", "observability", "api", "console", "ui"})
    return {
        1: ("修改范围", True),
        2: ("用户流程", user),
        3: ("运行过程", runtime),
        4: ("控制流程", control),
        5: ("状态变化", state),
        6: ("API 契约", api),
        7: ("数据库 / 持久化", db),
        8: ("外部依赖", ext),
        9: ("影响范围", bool(files)),
        10: ("测试与证据", bool(tests_changed)),
    }


def risk_model(files, units: list[ChangeUnit], tests_changed: list[str], dims):
    keys = {u.key for u in units}
    score = 0
    drivers = []
    def add(cond, name, pts):
        nonlocal score
        if cond:
            score += pts
            drivers.append((name, pts))
    add("auth" in keys, "登录 / 鉴权逻辑", 5)
    add("database" in keys, "数据库迁移或持久化", 5)
    add(dims[6][1], "公开 API 契约", 5)
    add("routing" in keys, "路由 / Channel 选择", 4)
    add("provider" in keys, "上游 Provider 调用", 4)
    add("streaming" in keys, "流式响应", 4)
    add("failover" in keys, "重试 / Failover", 4)
    add(dims[5][1] and bool(keys & {"auth","database","routing","provider","observability","failover"}), "关键状态写入", 3)
    production = any(is_runtime(f.path) for f in files)
    add(production and not tests_changed, "改了生产代码但这个提交没有同步改测试", 3)
    add(len(files) >= 30, "修改文件很多", 3)
    level = "高" if score >= 10 else "中" if score >= 5 else "低"
    return score, level, drivers


def unit_evidence(unit: ChangeUnit, base: str, target: str, limit: int = 6):
    out = []
    for i in unit.items:
        h = i.hunk
        if h.newn > 0 and i.new_path != "/dev/null":
            out.append(("修改后", target, i.new_path, h.new, max(h.new, h.new + h.newn - 1)))
        if h.oldn > 0 and i.old_path != "/dev/null":
            out.append(("修改前", base, i.old_path, h.old, max(h.old, h.old + h.oldn - 1)))
        if len(out) >= limit:
            break
    return out[:limit]


def blast_candidates(repo: Path, target: str, symbols, limit: int = 12):
    out = []
    for p, kind, name, ln in symbols[:6]:
        out.append(("直接修改", name, f"{p}:L{ln}"))
        if len(name) < 4:
            continue
        grep = run(repo, "grep", "-n", "-F", name, target, "--", "*.rs", check=False)
        for row in grep.splitlines()[:10]:
            m = re.match(r"([^:]+):(\d+):(.*)", row)
            if not m or m.group(1) == p:
                continue
            item = ("可能受影响（词法引用）", name, f"{m.group(1)}:L{m.group(2)}")
            if item not in out:
                out.append(item)
            if len(out) >= limit:
                return out
    return out[:limit]
