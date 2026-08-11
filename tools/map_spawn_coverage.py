from pathlib import Path
import json

CENSUS=Path('docs/entrypoint-census.json')
REPORT=Path('docs/coverage-report.md')
DOCS=Path('docs')


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

if __name__=='__main__': main()
