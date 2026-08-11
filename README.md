# burncloud.github.io

BurnCloud 的单页 **Entry Point Atlas**。

文档不再按旧的 Runtime Atlas / Commit Atlas 拆成大量页面。当前站点只有一个文档源：

- `docs/index.md` — 从可执行入口理解整个 BurnCloud：HTTP/API、CLI、Background Jobs、Startup、UI-only Actions。

站点使用 Docusaurus 构建，`docs/index.md` 映射到站点根路径 `/`。

## Truth source

页面内容以 `burncloud/burncloud` 当前源码为依据。文档内记录审计时使用的源码 commit；源码行为发生变化后，应重新核对入口表，而不是沿用旧描述。
