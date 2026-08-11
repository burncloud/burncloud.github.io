from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'; MANIFEST=DOCS/'atlas-manifest.json'; SIDEBAR=ROOT/'site'/'sidebars.js'

PAGES=[
    dict(section='Background Jobs / Async Side Effects',group='Long-running Jobs',title='Health Probe Scheduler',entry='Health Probe Scheduler',slug='/background/long-running-jobs/health-probe-scheduler',docid='background/long-running-jobs/health-probe-scheduler',sources=['crates/router/src/health_probe.rs'],explanation='ProbeScheduler::start() 启动 10 秒 ticker。当前源码的 scheduler loop 只记录 Probe scheduler tick，注释明确说明真正的 Half-Open channel 探测、Adaptor probe 和结果记录仍是待实现语义，因此不能把它描述成已经发送健康探测。'),
    dict(section='Background Jobs / Async Side Effects',group='Download Background Work',title='Aria2 Daemon Monitor',entry='Aria2 Daemon Monitor',slug='/background/download-background-work/aria2-daemon-monitor',docid='background/download-background-work/aria2-daemon-monitor',sources=['crates/download/crates/download-aria2/src/lib.rs'],explanation='Aria2Daemon::start() 内的 tokio::spawn 监控循环：每秒检查 aria2 child process；进程退出时调用 start_aria2_rpc() 尝试重新启动，stop() 将 running 置 false 后终止循环。'),
    dict(section='Background Jobs / Async Side Effects',group='Desktop Background Work',title='Windows Background Server Thread',entry='Windows Background Server Thread',slug='/background/desktop-background-work/windows-background-server-thread',docid='background/desktop-background-work/windows-background-server-thread',sources=['src/main.rs','crates/server/src/lib.rs'],explanation='Windows 下无参数启动 burncloud.exe 时，main() 创建 std::thread::spawn，在新 Tokio Runtime 中调用 burncloud_server::start_server(host, port, false)，同时主线程继续 launch_gui_with_tray()。'),
]

INSERT_AFTER={
    'Health Probe Scheduler':'        {type:\'doc\', id:"background/long-running-jobs/async-request-log-writer", label:"Async Request Log Writer"},',
    'Aria2 Daemon Monitor':'        {type:\'doc\', id:"background/download-background-work/restore-incomplete-downloads", label:"Restore incomplete downloads"},',
    'Windows Background Server Thread':'        {type:\'doc\', id:"background/desktop-background-work/show-window-poll-loop", label:"Show-window poll loop"},',
}


def base(p,sha):
    rows='\n'.join(f'| {i+1} | `{x}` |' for i,x in enumerate(p['sources']))
    return f'''---
title: "{p['title']}"
slug: {p['slug']}
hide_table_of_contents: true
---

# {p['title']}

**树路径：** `BurnCloud → {p['section']} → {p['group']} → {p['title']}`

> **中文解释：** {p['explanation']}
>
> **源码基线：** `burncloud/burncloud@{sha}`

## End-to-End Request Flow + ICFG

```text
START
│
├─ runtime trigger
│
▼
FILE: {p['sources'][0]}
│
├─ spawn background work
├─ DECISION: should continue?
│    ├─ YES → next iteration
│    └─ NO  → END
│
▼
END
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
{rows}

**Execution classification: STATIC CONFIRMED** — 本页来自运行时代码中的真实 background/thread 入口。
'''


def main():
    data=json.loads(MANIFEST.read_text(encoding='utf-8')); sidebar=SIDEBAR.read_text(encoding='utf-8'); existing={p['docid'] for p in data['pages']}; added=0
    for p in PAGES:
        if p['docid'] in existing: continue
        target=DOCS/(p['docid']+'.md'); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(base(p,data['source_sha']),encoding='utf-8')
        data['pages'].append({k:p[k] for k in ('section','group','title','entry','slug','docid')}); data['page_count']+=1; added+=1
        row=f'        {{type:\'doc\', id:"{p["docid"]}", label:"{p["title"]}"}},'; needle=INSERT_AFTER[p['title']]
        if row not in sidebar:
            if needle not in sidebar: raise RuntimeError(f'sidebar insertion point missing: {p["title"]}')
            sidebar=sidebar.replace(needle,needle+'\n'+row,1)
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); SIDEBAR.write_text(sidebar,encoding='utf-8')
    print(f'Added {added} background pages; page_count={data["page_count"]}')

if __name__=='__main__': main()
