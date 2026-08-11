from pathlib import Path
import re

FLOW_RE=re.compile(r'(## End-to-End Request Flow \+ ICFG\n\n)```text\n.*?\n```',re.S)
OUTPUT_RE=re.compile(r'## 返回结果示例\n\n> .*?\n\n```(?:text|json|http)\n.*?\n```',re.S)
SOURCE_RE=re.compile(r'## 穿过的源码文件\n\n\| 顺序 \| 文件 \|\n\|---\|---\|\n.*?(?=\n\n\*\*Execution classification:)',re.S)

ARIA_FLOW='''START
│
├─ OS / Shell 启动 binary: aria2-test
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ #[tokio::main] main()
├─ print "启动 BurnCloud Aria2 测试"
└─ CALL quick_start().await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ quick_start()
│    ├─ Aria2Manager::new()
│    ├─ download_and_setup()
│    │    └─ download_aria2()
│    │         ├─ DECISION: aria2c.exe already exists?
│    │         │    ├─ YES → reuse
│    │         │    └─ NO  → main download → fallback backup download
│    │         ├─ extract_aria2()
│    │         └─ DECISION: executable exists after extraction?
│    │              ├─ NO → Aria2Error::DownloadError → END
│    │              └─ YES → continue
│    └─ start_daemon()
│         └─ Aria2Daemon::start()
│              ├─ start_aria2_rpc()
│              ├─ store Aria2Instance
│              ├─ is_running = true
│              └─ tokio::spawn daemon monitor loop
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ manager.create_rpc_client()
├─ DECISION: RPC client exists?
│    ├─ NO → skip tests → cleanup
│    └─ YES
│         ├─ test_basic_operations()
│         │    ├─ get_global_stat() → aria2.getGlobalStat
│         │    └─ tell_active() → aria2.tellActive
│         └─ test_download()
│              └─ add_uri(test_url, DownloadOptions)
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2RpcClient::add_uri()
│    ├─ find_existing_task()
│    │    ├─ tell_active()
│    │    ├─ tell_waiting()
│    │    ├─ tell_stopped()
│    │    └─ tell_status() / get_files()
│    └─ DECISION: identical task exists?
│         ├─ YES → return existing gid
│         └─ NO  → call_method("aria2.addUri", ...)
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ DECISION: add_uri success?
│    ├─ NO → print error; continue cleanup
│    └─ YES → print gid → sleep → tell_status(gid)
├─ sleep 2 seconds
└─ manager.shutdown()
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Manager::shutdown()
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill child process
│         └─ clear instance
│
▼
END
'''

HEALTH_FLOW='''START
│
├─ Router runtime creates ProbeScheduler
└─ CALL ProbeScheduler::start()
│
▼
FILE: crates/router/src/health_probe.rs
│
├─ ProbeScheduler::start()
│    ├─ running.swap(true)
│    └─ DECISION: already running?
│         ├─ YES → return immediately → END
│         └─ NO  → clone manager + running flag
│
├─ tokio::spawn(async move { ... })
│    ├─ ticker = interval(10 seconds)
│    └─ WHILE running == true
│         ├─ ticker.tick().await
│         ├─ tracing::debug!("Probe scheduler tick")
│         └─ next iteration
│
├─ IMPORTANT CURRENT SOURCE LIMIT
│    ├─ comments describe intended Half-Open channel discovery
│    ├─ comments describe intended adaptor probe send
│    └─ those operations are NOT implemented inside the current scheduler loop
│
├─ Stop path
│    └─ ProbeScheduler::stop() → running = false
│
▼
END / NEXT TICK
'''

ARIA_MONITOR='''START
│
├─ Aria2Manager::start_daemon()
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Daemon::start()
│    ├─ DECISION: is_running already true?
│    │    ├─ YES → DaemonError → END
│    │    └─ NO → start_aria2_rpc()
│    ├─ save Aria2Instance in Arc<Mutex<Option<_>>>
│    ├─ is_running = true
│    └─ tokio::spawn monitor task
│
├─ Monitor loop
│    ├─ WHILE is_running == true
│    ├─ sleep 1000 ms
│    ├─ lock instance
│    └─ DECISION: aria2 child process still running?
│         ├─ YES → next iteration
│         └─ NO
│              ├─ print restart message
│              ├─ CALL start_aria2_rpc(&config)
│              └─ DECISION: restart succeeds?
│                   ├─ NO → keep loop alive; retry on later iteration
│                   └─ YES → replace stored Aria2Instance
│
├─ Stop path
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill existing child
│         └─ instance = None
│
▼
END / NEXT ITERATION
'''

WINDOWS_SERVER='''START
│
├─ User launches burncloud.exe with no CLI arguments on Windows
│
▼
FILE: src/main.rs
│
├─ main()
│    ├─ dotenvy::dotenv()
│    ├─ ensure_master_key()
│    ├─ init_logging()
│    └─ DECISION: args == [binary] AND target_os == windows?
│         ├─ NO → other CLI/server/client branch
│         └─ YES → std::thread::spawn server thread
│
├─ Background OS thread
│    ├─ tokio::runtime::Runtime::new()
│    ├─ read HOST or default 127.0.0.1
│    ├─ read PORT or DEFAULT_PORT
│    └─ rt.block_on(burncloud_server::start_server(host, port, false))
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server(host, port, enable_liveview=false)
│    ├─ create_default_database()
│    ├─ RouterDatabase::init()
│    ├─ UserDatabase::init()
│    ├─ create_app(db, false)
│    ├─ TcpListener::bind()
│    └─ axum::serve()
│
├─ DECISION: server startup/runtime returns Err?
│    ├─ YES → src/main.rs thread prints "Server failed to start"
│    └─ NO → server thread remains serving requests
│
▼
FILE: src/main.rs
│
└─ Main Windows thread independently continues
     └─ burncloud_client::launch_gui_with_tray()
│
▼
END / SERVER THREAD CONTINUES
'''

ARIA_OUTPUT='''## 返回结果示例

> 以下为构造的典型成功终端输出；端口、GID、下载速度和文件大小由实际 aria2 运行状态决定。

```text
🚀 启动 BurnCloud Aria2 测试...
aria2 RPC 服务已启动在端口: 6800
aria2 守护进程启动成功！
✅ Aria2 管理器启动成功
📡 获取到 RPC 客户端
🔍 测试基本操作...
  - 活跃下载: 0
  - 等待下载: 0
📥 测试下载功能...
  - 添加下载任务成功，GID: 2089b05ecca3d829
  - 任务状态: active
Aria2Manager 已关闭
🛑 测试完成，管理器已关闭
```'''

CONFIG={
 'docs/cli/workspace-binaries/aria2-test.md':(ARIA_FLOW,ARIA_OUTPUT,['crates/download/crates/download-aria2/src/main.rs','crates/download/crates/download-aria2/src/lib.rs']),
 'docs/background/long-running-jobs/health-probe-scheduler.md':(HEALTH_FLOW,None,['crates/router/src/health_probe.rs']),
 'docs/background/download-background-work/aria2-daemon-monitor.md':(ARIA_MONITOR,None,['crates/download/crates/download-aria2/src/lib.rs']),
 'docs/background/desktop-background-work/windows-background-server-thread.md':(WINDOWS_SERVER,None,['src/main.rs','crates/server/src/lib.rs']),
}


def simple_source(files):
    rows='\n'.join(f'| {i+1} | `{f}` |' for i,f in enumerate(files))
    return '## 穿过的源码文件\n\n| 顺序 | 文件 |\n|---|---|\n'+rows


def fix(path_s,flow,output,files):
    path=Path(path_s); text=path.read_text(encoding='utf-8')
    text,n=FLOW_RE.subn(r'\1```text\n'+flow.rstrip()+'\n```',text,count=1)
    if n!=1: raise RuntimeError(f'flow block not found: {path}')
    if output:
        text,n=OUTPUT_RE.subn(output,text,count=1)
        if n!=1: raise RuntimeError(f'output block not found: {path}')
    text,n=SOURCE_RE.subn(simple_source(files),text,count=1)
    if n!=1: raise RuntimeError(f'source table not found: {path}')
    path.write_text(text,encoding='utf-8')


def main():
    for args in CONFIG.items(): fix(args[0],*args[1])
    print(f'Deepened {len(CONFIG)} census-discovered flows')

if __name__=='__main__': main()
