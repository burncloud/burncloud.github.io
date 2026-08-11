from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from collections import defaultdict

METHOD_FN = {"get":"GET","post":"POST","put":"PUT","delete":"DELETE","patch":"PATCH"}
NON_RUNTIME_PARTS = ("crates/tests/", "/tests/", "examples/", "benches/", "/target/")


def is_non_runtime_path(rel: str) -> bool:
    wrapped = "/" + rel
    return any(x in wrapped for x in NON_RUNTIME_PARTS)


def strip_rust_comments(text: str) -> str:
    """Remove // and /* */ comments while preserving strings and newlines.

    This prevents commented-out future routes from being counted as executable
    entrypoints. Newlines are retained so source line numbers stay meaningful.
    """
    out=[]
    i=0
    n=len(text)
    state="code"
    block_depth=0
    while i<n:
        ch=text[i]
        nxt=text[i+1] if i+1<n else ""
        if state=="code":
            if ch=='"':
                state="string"; out.append(ch); i+=1
            elif ch=="'":
                # Rust char/lifetime syntax is awkward; preserving it is safer
                # than treating it as a comment boundary.
                out.append(ch); i+=1
            elif ch=='/' and nxt=='/':
                state="line_comment"; out.extend("  "); i+=2
            elif ch=='/' and nxt=='*':
                state="block_comment"; block_depth=1; out.extend("  "); i+=2
            else:
                out.append(ch); i+=1
        elif state=="string":
            out.append(ch)
            if ch=='\\' and i+1<n:
                out.append(text[i+1]); i+=2
            elif ch=='"':
                state="code"; i+=1
            else:
                i+=1
        elif state=="line_comment":
            if ch=='\n':
                out.append('\n'); state="code"
            else:
                out.append(' ')
            i+=1
        else:  # block_comment
            if ch=='/' and nxt=='*':
                block_depth+=1; out.extend("  "); i+=2
            elif ch=='*' and nxt=='/':
                block_depth-=1; out.extend("  "); i+=2
                if block_depth==0: state="code"
            else:
                out.append('\n' if ch=='\n' else ' '); i+=1
    return ''.join(out)


def iter_route_calls(text: str):
    needle=".route("
    pos=0
    while True:
        start=text.find(needle,pos)
        if start<0: return
        i=start+len(needle)
        depth=1; in_string=False; escape=False
        while i<len(text) and depth:
            ch=text[i]
            if in_string:
                if escape: escape=False
                elif ch=='\\': escape=True
                elif ch=='"': in_string=False
            else:
                if ch=='"': in_string=True
                elif ch=='(': depth+=1
                elif ch==')': depth-=1
            i+=1
        if depth==0:
            yield start,text[start+len(needle):i-1]
            pos=i
        else:
            return


def line_no(text:str,offset:int)->int:
    return text.count('\n',0,offset)+1


def normalize_http_path(path:str)->str:
    # Only normalize a Dioxus-style colon parameter when ':' begins a path
    # segment. Do NOT alter Gemini action suffixes such as {model}:countTokens.
    return re.sub(r'(?<=/):([A-Za-z_][A-Za-z0-9_]*)',r'{\1}',path)


def parse_http_routes(source:Path):
    found=[]
    for f in source.rglob('*.rs'):
        rel=f.relative_to(source).as_posix()
        if is_non_runtime_path(rel): continue
        raw=f.read_text(encoding='utf-8',errors='ignore')
        text=strip_rust_comments(raw)
        for offset,body in iter_route_calls(text):
            m=re.match(r'\s*"([^"]+)"\s*,(.*)',body,re.S)
            if not m: continue
            path,expr=normalize_http_path(m.group(1)),m.group(2)
            methods=[]
            for fn,method in METHOD_FN.items():
                if re.search(rf'(?:\b|::|\.){fn}\s*\(',expr): methods.append(method)
            if not methods: methods=['UNKNOWN']
            handlers=sorted(set(re.findall(r'(?:get|post|put|delete|patch)\s*\(\s*([A-Za-z_][A-Za-z0-9_:]*)',expr)))
            for method in methods:
                found.append({"method":method,"path":path,"entry":f"{method} {path}","file":rel,"line":line_no(text,offset),"handlers":handlers})
    return found


def parse_dioxus_routes(source:Path):
    found=[]
    for f in source.rglob('*.rs'):
        rel=f.relative_to(source).as_posix()
        if is_non_runtime_path(rel): continue
        text=strip_rust_comments(f.read_text(encoding='utf-8',errors='ignore'))
        for m in re.finditer(r'#\[route\(\s*"([^"]+)"\s*\)\]',text):
            found.append({"path":m.group(1),"file":rel,"line":line_no(text,m.start())})
    return found


def parse_spawn_sites(source:Path):
    found=[]
    pats=[('tokio::spawn',r'tokio::spawn\s*\('),('tokio::task::spawn',r'tokio::task::spawn\s*\('),('std::thread::spawn',r'std::thread::spawn\s*\(')]
    for f in source.rglob('*.rs'):
        rel=f.relative_to(source).as_posix()
        if is_non_runtime_path(rel): continue
        raw=f.read_text(encoding='utf-8',errors='ignore')
        text=strip_rust_comments(raw)
        for kind,pat in pats:
            for m in re.finditer(pat,text):
                ctx=text[max(0,m.start()-160):min(len(text),m.start()+220)].replace('\n',' ')
                found.append({"file":rel,"line":line_no(text,m.start()),"kind":kind,"context":re.sub(r'\s+',' ',ctx).strip()})
    return found


def cargo_package_name(cargo:Path):
    if not cargo.exists(): return None
    text=strip_rust_comments(cargo.read_text(encoding='utf-8',errors='ignore'))
    m=re.search(r'(?ms)^\[package\].*?^name\s*=\s*"([^"]+)"',text)
    return m.group(1) if m else None


def explicit_bins(cargo:Path):
    if not cargo.exists(): return []
    text=cargo.read_text(encoding='utf-8',errors='ignore')
    out=[]
    for block in re.findall(r'(?ms)^\[\[bin\]\](.*?)(?=^\[|\Z)',text):
        name=re.search(r'(?m)^name\s*=\s*"([^"]+)"',block)
        path=re.search(r'(?m)^path\s*=\s*"([^"]+)"',block)
        if name and path: out.append((name.group(1),path.group(1)))
    return out


def parse_binaries(source:Path):
    out=[]; seen=set()
    for cargo in source.rglob('Cargo.toml'):
        relcargo=cargo.relative_to(source).as_posix()
        if is_non_runtime_path(relcargo): continue
        base=cargo.parent
        pkg=cargo_package_name(cargo)
        explicit=explicit_bins(cargo)
        explicit_paths={p for _,p in explicit}
        for name,p in explicit:
            f=base/p
            if f.exists():
                rel=f.relative_to(source).as_posix(); key=(name,rel)
                if key not in seen: out.append({"name":name,"file":rel,"kind":"explicit-bin"}); seen.add(key)
        main=base/'src/main.rs'
        if main.exists() and 'src/main.rs' not in explicit_paths:
            name=pkg or base.name
            rel=main.relative_to(source).as_posix(); key=(name,rel)
            if key not in seen: out.append({"name":name,"file":rel,"kind":"package-main"}); seen.add(key)
        bindir=base/'src/bin'
        if bindir.is_dir():
            for f in bindir.glob('*.rs'):
                rel=f.relative_to(source).as_posix(); key=(f.stem,rel)
                if key not in seen: out.append({"name":f.stem,"file":rel,"kind":"src-bin"}); seen.add(key)
    return sorted(out,key=lambda x:(x['file'],x['name']))


def manifest_http_entries(manifest):
    out=set()
    for p in manifest['pages']:
        if p['section']!='HTTP / API': continue
        m=re.match(r'^(GET|POST|PUT|DELETE|PATCH)\s+([^\s]+)',p['entry'])
        if m: out.add(f"{m.group(1)} {normalize_http_path(m.group(2))}")
    return out


def manifest_ui_routes(manifest):
    out=set()
    for p in manifest['pages']:
        if p['section']!='UI-only Actions': continue
        if p['group'] not in ('Guest / Public','Console','Debug / e2e-preview'): continue
        route=p['entry'].split(' → ',1)[0]
        out.add(route)
    return out


def binary_coverage(binaries,docs_root:Path):
    corpus='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in docs_root.rglob('*.md'))
    covered=[]; missing=[]
    for b in binaries:
        (covered if b['file'] in corpus else missing).append(b)
    return covered,missing


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--manifest',default='docs/atlas-manifest.json')
    ap.add_argument('--json',default='docs/entrypoint-census.json')
    ap.add_argument('--report',default='docs/coverage-report.md')
    args=ap.parse_args()
    source=Path(args.source).resolve(); manifest_path=Path(args.manifest)
    docs_root=manifest_path.parent
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')); source_sha=manifest['source_sha']

    http=parse_http_routes(source); dioxus=parse_dioxus_routes(source); spawns=parse_spawn_sites(source); binaries=parse_binaries(source)
    documented_http=manifest_http_entries(manifest)
    runtime_http={r['entry'] for r in http if r['method']!='UNKNOWN'}
    covered_http=sorted(runtime_http & documented_http); missing_http=sorted(runtime_http-documented_http)
    documented_not_scanned=sorted(documented_http-runtime_http)
    by_entry=defaultdict(list)
    for r in http: by_entry[r['entry']].append(r)

    app_ui={r['path'] for r in dioxus if r['file']=='crates/client/src/app.rs'}
    doc_ui=manifest_ui_routes(manifest)
    covered_ui=sorted(app_ui & doc_ui); missing_ui=sorted(app_ui-doc_ui); extra_ui=sorted(doc_ui-app_ui)
    binary_covered,binary_missing=binary_coverage(binaries,docs_root)

    counts={
        'http_route_declarations':len(http),
        'http_unique_entries':len(runtime_http),
        'http_documented_exact_matches':len(covered_http),
        'http_missing_exact_matches':len(missing_http),
        'main_dioxus_unique_routes':len(app_ui),
        'ui_documented_exact_matches':len(covered_ui),
        'ui_missing_exact_matches':len(missing_ui),
        'binary_source_entries':len(binaries),
        'binary_documented_source_matches':len(binary_covered),
        'binary_missing_source_matches':len(binary_missing),
        'runtime_spawn_sites':len(spawns),
    }
    result={
        'source_sha':source_sha,'manifest_page_count':manifest['page_count'],'counts':counts,
        'missing_http_entries':[{'entry':e,'declarations':by_entry[e]} for e in missing_http],
        'documented_http_not_seen_as_direct_axum_route':documented_not_scanned,
        'missing_main_ui_routes':missing_ui,'documented_ui_not_in_main_app':extra_ui,
        'missing_binary_entries':binary_missing,
        'http_routes':http,'dioxus_routes':dioxus,'binaries':binaries,'spawn_sites':spawns,
    }
    Path(args.json).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=['---','title: "Coverage / Entry Point Census"','slug: /coverage-report','---','',
           '# BurnCloud Entry Point Census','',
           f'> 源码基线：`burncloud/burncloud@{source_sha}`。本页由 CI 从真实源码扫描生成；HTTP、主 Dioxus 路由、Binary 的缺失数量必须为 0 才允许发布。','',
           '## 汇总','', '| 项目 | 数量 |','|---|---:|']
    for k,v in counts.items(): lines.append(f'| `{k}` | {v} |')
    lines += ['', '## HTTP Coverage','']
    if not missing_http: lines.append('**Missing = 0。** 扫描到的直接 Axum Method + Path 声明均有 Atlas 覆盖。')
    else:
        lines += ['| Missing Entry | Source |','|---|---|']
        for e in missing_http:
            locs=', '.join(f"`{x['file']}:{x['line']}`" for x in by_entry[e]); lines.append(f'| `{e}` | {locs} |')
    lines += ['', '### Atlas 中的 fallback / 组合 / 语义 HTTP Entry','',
              '> 下列项目不一定对应直接 `.route()`；常见于 router fallback、LiveView 组合路由、动态路径或兼容入口，因此单列人工审计。','']
    for e in documented_not_scanned: lines.append(f'- `{e}`')

    lines += ['', '## Main Dioxus UI Coverage','']
    if not missing_ui: lines.append('**Missing = 0。** `crates/client/src/app.rs` 的主 Route 集合均有 UI-only Atlas 页面。')
    else:
        for x in missing_ui: lines.append(f'- MISSING `{x}`')
    if extra_ui:
        lines += ['', 'Atlas 中未直接出现在 main app Route enum 的 UI 语义项：']
        for x in extra_ui: lines.append(f'- `{x}`')

    lines += ['', '## Binary Coverage','', '| Binary | Source | Coverage |','|---|---|---|']
    missing_files={x['file'] for x in binary_missing}
    for b in binaries: lines.append(f"| `{b['name']}` | `{b['file']}` | {'MISSING' if b['file'] in missing_files else 'COVERED'} |")

    lines += ['', '## Runtime Async Spawn Sites','',
              f'排除 tests/examples/benches 后，共扫描到 **{len(spawns)}** 个运行时代码 `spawn` 站点。它们作为 Background / async side-effect 人工覆盖审计清单。','',
              '| Source | Line | Kind |','|---|---:|---|']
    for s in spawns: lines.append(f"| `{s['file']}` | {s['line']} | `{s['kind']}` |")

    lines += ['', '## 全部主 Dioxus Route 源码位置','', '| Route | Source |','|---|---|']
    for r in dioxus:
        if r['file']=='crates/client/src/app.rs': lines.append(f"| `{r['path']}` | `{r['file']}:{r['line']}` |")
    Path(args.report).write_text('\n'.join(lines)+'\n',encoding='utf-8')

    print(json.dumps(counts,ensure_ascii=False))
    for label,items in [('MISSING_HTTP',missing_http),('MISSING_UI',missing_ui)]:
        if items:
            print(label+':'); [print(' -',x) for x in items]
    if binary_missing:
        print('MISSING_BINARIES:'); [print(' -',x['name'],x['file']) for x in binary_missing]


if __name__=='__main__': main()
