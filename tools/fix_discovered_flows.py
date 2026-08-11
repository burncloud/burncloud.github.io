from pathlib import Path
import re

PAGE = Path('docs/cli/workspace-binaries/aria2-test.md')
FLOW_RE = re.compile(r'(## End-to-End Request Flow \+ ICFG\n\n)```text\n.*?\n```', re.S)
OUTPUT_RE = re.compile(r'## 返回结果示例\n\n> .*?\n\n```text\n.*?\n```', re.S)
SOURCE_RE = re.compile(r'## 穿过的源码文件\n\n\| 顺序 \| 文件 \|\n\|---\|---\|\n.*?(?=\n\n\*\*Execution classification:)', re.S)

FLOW = '''START
│
├─ OS / Shell 启动 binary
│    └─ aria2-test
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
│    ├─ manager.download_and_setup().await
│    └─ manager.start_daemon().await
│
├─ Aria2Manager::download_and_setup()
│    └─ download_aria2()
│         ├─ determine BurnCloud local directory
│         ├─ DECISION: aria2c.exe already exists?
│         │    ├─ YES → reuse existing binary
│         │    └─ NO  → download main URL
│         │         └─ DECISION: main download succeeds?
│         │              ├─ YES → extract ZIP
│         │              └─ NO  → try backup URL → extract ZIP
│         └─ DECISION: extracted aria2c.exe exists?
│              ├─ NO → Aria2Error::DownloadError → END
│              └─ YES → return executable path
│
├─ Aria2Manager::start_daemon()
│    ├─ DECISION: daemon already exists?
│    │    ├─ YES → Aria2Error::DaemonError → END
│    │    └─ NO  → Aria2Daemon::new(...)
│    └─ Aria2Daemon::start().await
│         ├─ start_aria2_rpc(&config)
│         ├─ persist Aria2Instance in Arc<Mutex<Option<_>>>
│         ├─ is_running = true
│         └─ tokio::spawn daemon monitor loop
│              ├─ sleep 1 second
│              ├─ DECISION: aria2 child still running?
│              │    ├─ YES → continue monitoring
│              │    └─ NO  → start_aria2_rpc() restart attempt
│              └─ repeat while is_running
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ manager.create_rpc_client()
└─ DECISION: RPC client available?
     ├─ NO  → skip RPC tests → shutdown
     └─ YES → test_basic_operations(&client)
│
├─ test_basic_operations()
│    ├─ client.get_global_stat().await
│    │    └─ JSON-RPC aria2.getGlobalStat
│    └─ client.tell_active().await
│         └─ JSON-RPC aria2.tellActive
│
├─ test_download()
│    ├─ construct DownloadOptions { dir: "./downloads", ... }
│    └─ client.add_uri(test_url, options).await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2RpcClient::add_uri()
│    ├─ find_existing_task(...)
│    │    ├─ tell_active()
│    │    ├─ tell_waiting()
│    │    ├─ tell_stopped()
│    │    └─ tell_status() / get_files() when checking duplicates
│    └─ DECISION: identical task already exists?
│         ├─ YES → return existing gid
│         └─ NO  → call_method("aria2.addUri", ...)
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ DECISION: add_uri succeeded?
│    ├─ NO  → print failure, continue cleanup
│    └─ YES
│         ├─ print GID
│         ├─ sleep 1 second
│         └─ client.tell_status(&gid)
│
├─ sleep 2 seconds
└─ manager.shutdown().await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Manager::shutdown()
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill aria2 child process if present
│         └─ clear daemon instance
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ print "测试完成，管理器已关闭"
└─ return Ok(())
│
▼
END
'''

OUTPUT = '''## 返回结果示例

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
  - 下载速度: 0
  - 当前活跃任务数: 0
📥 测试下载功能...
  - 添加下载任务成功，GID: 2089b05ecca3d829
  - 任务状态: active
Aria2Manager 已关闭
🛑 测试完成，管理器已关闭
```
'''

SOURCE = '''## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/download/crates/download-aria2/src/main.rs` |
| 2 | `crates/download/crates/download-aria2/src/lib.rs` |'''


def main():
    text=PAGE.read_text(encoding='utf-8')
    text,n=FLOW_RE.subn(r'\1```text\n'+FLOW.rstrip()+'\n```',text,count=1)
    if n!=1: raise RuntimeError('aria2-test flow block not found')
    text,n=OUTPUT_RE.subn(OUTPUT.rstrip(),text,count=1)
    if n!=1: raise RuntimeError('aria2-test output block not found')
    text,n=SOURCE_RE.subn(SOURCE,text,count=1)
    if n!=1: raise RuntimeError('aria2-test source table not found')
    PAGE.write_text(text,encoding='utf-8')
    print('Deepened aria2-test flow and source traversal seed')

if __name__=='__main__': main()
