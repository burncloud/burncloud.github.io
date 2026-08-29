from pathlib import Path
import base64
import json
import os
import re
import subprocess
import sys

CENSUS=Path('docs/entrypoint-census.json')
REPORT=Path('docs/coverage-report.md')
DOCS=Path('docs')
SIDEBAR=Path('site/sidebars.js')


def map_site(s):
    f=s['file']; c=s.get('context','')
    if f=='src/main.rs': return 'background/desktop-background-work/windows-background-server-thread'
    if f=='crates/router/src/lib.rs':
        if 'start_sync_task' in c or 'exch_clone' in c: return 'background/long-running-jobs/exchange-rate-sync'
        if 'budget-update' in c or 'budget_update_rx' in c: return 'background/long-running-jobs/aimd-budget-feedback'
        if 'Logging task started' in c: return 'background/long-running-jobs/async-router-log-writer'
        if 'Request logging task' in c or 'request_log_rx' in c: return 'background/long-running-jobs/async-request-log-writer'
        if 'update_token_accessed_time' in c: return 'background/request-time-async-side-effects/token-accessed_time-update'
        if 'RouterVideoTaskModel::save' in c: return 'background/request-time-async-side-effects/video-task-mapping-save'
        if 'deduct_quota' in c: return 'background/request-time-async-side-effects/quota-deduction'
        if 'detect_and_update' in c: return 'background/request-time-async-side-effects/api-version-detect-update'
    if f=='crates/router/src/health_probe.rs': return 'background/long-running-jobs/health-probe-scheduler'
    if f=='crates/router/src/exchange_rate.rs': return 'background/long-running-jobs/exchange-rate-sync'
    if f=='crates/router/src/price_sync.rs': return 'background/long-running-jobs/price-sync'
    if f=='crates/download/src/lib.rs': return 'background/download-background-work/download-progress-monitor'
    if f=='crates/download/crates/download-aria2/src/lib.rs': return 'background/download-background-work/aria2-daemon-monitor'
    if f=='crates/service/crates/monitor/src/service.rs': return 'background/long-running-jobs/system-monitor-auto-update'
    if f=='crates/client/src/app.rs': return 'background/desktop-background-work/windows-tray-thread'
    return None


def checkout_github_token():
    """Reuse actions/checkout's already-configured token without printing it."""
    try:
        raw=subprocess.check_output(
            ['git','config','--local','--get','http.https://github.com/.extraheader'],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        prefix='authorization: basic '
        if not raw.lower().startswith(prefix):
            return ''
        encoded=raw[len(prefix):].strip()
        decoded=base64.b64decode(encoded).decode('utf-8')
        if ':' not in decoded:
            return ''
        return decoded.split(':',1)[1]
    except Exception:
        return ''


def normalize_sidebar_layout():
    """Keep generated reference categories closed before product docs are injected."""
    text=SIDEBAR.read_text(encoding='utf-8')
    start='    // PR_CHANGE_ATLAS_START\n'
    end='    // PR_CHANGE_ATLAS_END\n'
    pattern=re.compile(re.escape(start)+r'.*?'+re.escape(end), flags=re.S)
    match=pattern.search(text)
    if not match:
        raise RuntimeError('PR Change Atlas sidebar block not found')

    pr_block=match.group(0).replace('collapsed:false','collapsed:true')
    text=pattern.sub('', text, count=1)
    text=text.replace('collapsed:false','collapsed:true')

    trailer='  ],\n};'
    if trailer not in text:
        raise RuntimeError('docsSidebar closing marker not found')
    text=text.replace(trailer, pr_block+trailer, 1)
    SIDEBAR.write_text(text, encoding='utf-8')


def generate_pr_change_atlas_in_ci():
    # This hook intentionally runs at the very end of the source-enrichment chain.
    # PR pages therefore embed the final V4 E2E/ICFG text, not the early generic flow.
    # Keep local standalone spawn-census runs network-free.
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        return
    env=os.environ.copy()
    if not env.get('GITHUB_TOKEN'):
        token=checkout_github_token()
        if token:
            env['GITHUB_TOKEN']=token
    subprocess.run(
        [sys.executable, 'tools/generate_pr_atlas.py', '--limit', '50'],
        check=True,
        env=env,
    )
    normalize_sidebar_layout()
    subprocess.run(
        [sys.executable, 'tools/generate_product_docs.py'],
        check=True,
    )
    pr_files=sorted((DOCS/'pr').glob('pr-*.md'))
    if len(pr_files) != 50:
        raise RuntimeError(f'expected 50 PR markdown files, got {len(pr_files)}')
    manifest=json.loads((DOCS/'pr-atlas-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('pr_count') != 50:
        raise RuntimeError(f"expected pr_count=50, got {manifest.get('pr_count')}")
    for p in pr_files:
        text=p.read_text(encoding='utf-8')
        for needle in ['## PR 影响总览','## Changed Files','## Affected E2E Impact Matrix','## 完整受影响 E2E Request Flow','## Execution Classification']:
            if needle not in text:
                raise RuntimeError(f'{p}: missing {needle}')
    print('PR Change Atlas: generated and validated 50 pages')


def main():
    data=json.loads(CENSUS.read_text(encoding='utf-8'))
    mapped=[];unmapped=[]
    for s in data['spawn_sites']:
        docid=map_site(s)
        if docid and (DOCS/(docid+'.md')).is_file():
            item=dict(s); item['docid']=docid; mapped.append(item)
        else:
            item=dict(s); item['candidate_docid']=docid; unmapped.append(item)
    data['spawn_coverage']={'mapped':mapped,'unmapped':unmapped}
    data['counts']['runtime_spawn_mapped']=len(mapped)
    data['counts']['runtime_spawn_unmapped']=len(unmapped)
    CENSUS.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    report=REPORT.read_text(encoding='utf-8')
    lines=['','## Runtime Spawn → Background Page Coverage','',
           f'扫描到的 runtime spawn 共 **{len(mapped)+len(unmapped)}** 个；已映射 **{len(mapped)}**，未映射 **{len(unmapped)}**。','',
           '| Source | Line | Background Atlas Page |','|---|---:|---|']
    for s in mapped:
        lines.append(f"| `{s['file']}` | {s['line']} | `{s['docid']}` |")
    if unmapped:
        lines += ['','### 未映射 spawn','']
        for s in unmapped: lines.append(f"- `{s['file']}:{s['line']}` — `{s.get('context','')[:180]}`")
    REPORT.write_text(report.rstrip()+'\n'+'\n'.join(lines)+'\n',encoding='utf-8')
    print(f'runtime spawn coverage: mapped={len(mapped)} unmapped={len(unmapped)}')
    if unmapped:
        for s in unmapped: print('UNMAPPED',s['file'],s['line'],s.get('context','')[:180])

    generate_pr_change_atlas_in_ci()

if __name__=='__main__': main()
