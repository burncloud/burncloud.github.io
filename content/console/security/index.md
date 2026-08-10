---
title: "Security Monitor Actions"
slug: /console/security/
type: runtime-flow
flow_id: user.console.security
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "/console/api/monitor/security*"
---

# Security Monitor Actions

← [Console 管理](/console/)

## What happens here?

Security routes include summary/events/filter configuration plus emergency circuit-break action. Some handlers call Router internal HTTP endpoints through loopback `127.0.0.1:{PORT}` and optionally attach `X-Internal-Secret`; therefore the Console Security layer can trigger an internal Router operation through a real HTTP hop rather than a direct Rust function call.

## ICFG — Internal Router Call Helper

```mermaid
flowchart TD
    E["Security handler needs Router internal state/action"] --> P["build http://127.0.0.1:{PORT}{path}"]
    R["reqwest Client GET/POST + timeout"]
    SEC{"BURNCLOUD_INTERNAL_SECRET set?"}
    H["Add X-Internal-Secret"]
    SEND["send().await"]
    ST{"HTTP success?"}
    JSON["Parse JSON and return"]
    ERR["Return router call error"]
    E --> P --> R --> SEC
    SEC -->|Yes| H --> SEND
    SEC -->|No| SEND
    SEND --> ST
    ST -->|Yes| JSON
    ST -->|No| ERR
    click R "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/security.rs#L117" "Open internal call helper" _blank
```

## Source Evidence

- Routes: [`crates/server/src/api/security.rs:L95-L113`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/security.rs#L95-L113)
- Internal GET helper: [`crates/server/src/api/security.rs:L117-L146`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/security.rs#L117-L146)
- Internal POST helper: [`crates/server/src/api/security.rs:L148-L183`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/security.rs#L148-L183)

**Confidence: HIGH — STATIC CONFIRMED**
