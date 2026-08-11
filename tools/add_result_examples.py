from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFEST = DOCS / "atlas-manifest.json"
MARKER = "\n## 穿过的源码文件\n"


def fenced(lang: str, body: str) -> str:
    return f"```{lang}\n{body.rstrip()}\n```"


def section(example: str, note: str = "以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。") -> str:
    return f"\n## 返回结果示例\n\n> {note}\n\n{example}\n\n"


def http_json(obj, status="HTTP/1.1 200 OK"):
    payload = json.dumps(obj, ensure_ascii=False, indent=2)
    return fenced("http", f"{status}\nContent-Type: application/json\n\n{payload}")


def http_text(text, status="HTTP/1.1 200 OK", content_type="text/plain; charset=utf-8"):
    return fenced("http", f"{status}\nContent-Type: {content_type}\n\n{text}")


def http_example(p):
    entry = p["entry"]
    title = p["title"]
    group = p["group"]
    low = entry.lower()

    # AI API / Data Plane
    if entry == "GET /v1/models":
        return http_json({
            "object": "list",
            "data": [
                {"id": "gpt-5.4", "object": "model", "created": 1786380000, "owned_by": "burncloud", "permission": [], "root": "gpt-5.4", "parent": None},
                {"id": "claude-sonnet-4-5", "object": "model", "created": 1786380000, "owned_by": "burncloud", "permission": [], "root": "claude-sonnet-4-5", "parent": None}
            ]
        })
    if entry in ("GET /api/v1/usage",):
        return http_json({
            "period": "month",
            "requests": 12842,
            "prompt_tokens": 18420560,
            "completion_tokens": 6912840,
            "total_tokens": 25333400,
            "cost": 126.67
        })
    if entry in ("GET /api/v1/usage/models",):
        return http_json({
            "period": "month",
            "models": [
                {"model": "gpt-5.4", "requests": 8021, "total_tokens": 16600420, "cost": 81.24},
                {"model": "claude-sonnet-4-5", "requests": 4821, "total_tokens": 8732980, "cost": 45.43}
            ]
        })
    if entry in ("POST /v1/chat/completions", "POST /chat/completions"):
        return http_json({
            "id": "chatcmpl_bc_01JXYZ",
            "object": "chat.completion",
            "created": 1786380000,
            "model": "gpt-5.4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "你好，我已经收到你的请求。"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 18, "completion_tokens": 14, "total_tokens": 32}
        })
    if entry == "POST /v1/completions":
        return http_json({
            "id": "cmpl_bc_01JXYZ",
            "object": "text_completion",
            "created": 1786380000,
            "model": "gpt-5.4",
            "choices": [{"text": "BurnCloud 已完成本次补全。", "index": 0, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 9, "total_tokens": 21}
        })
    if entry == "POST /v1/embeddings":
        return http_json({
            "object": "list",
            "data": [{"object": "embedding", "index": 0, "embedding": [0.0124, -0.0431, 0.0088, 0.0912]}],
            "model": "text-embedding-3-large",
            "usage": {"prompt_tokens": 8, "total_tokens": 8}
        })
    if entry == "POST /v1/messages":
        return http_json({
            "id": "msg_bc_01JXYZ",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-5",
            "content": [{"type": "text", "text": "这是通过 BurnCloud 转发后的 Anthropic 原生响应示例。"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 22, "output_tokens": 18}
        })
    if entry == "POST /v1/video/generations":
        return http_json({
            "id": "video_task_bc_01JXYZ",
            "object": "video.generation",
            "status": "queued",
            "model": "video-model-pro",
            "created": 1786380000
        }, "HTTP/1.1 202 Accepted")
    if entry.startswith("GET /v1/videos/"):
        return http_json({
            "id": "video_task_bc_01JXYZ",
            "object": "video.generation",
            "status": "completed",
            "model": "video-model-pro",
            "output": [{"url": "https://example.invalid/videos/video_task_bc_01JXYZ.mp4"}],
            "duration": 5,
            "resolution": "1080p"
        })
    if ":generateContent" in entry:
        return http_json({
            "candidates": [{"content": {"role": "model", "parts": [{"text": "这是 Gemini 原生 generateContent 返回示例。"}]}, "finishReason": "STOP", "index": 0}],
            "usageMetadata": {"promptTokenCount": 16, "candidatesTokenCount": 13, "totalTokenCount": 29},
            "modelVersion": "gemini-example"
        })
    if ":streamGenerateContent" in entry:
        body = """data: {\"candidates\":[{\"content\":{\"role\":\"model\",\"parts\":[{\"text\":\"这是\"}]},\"index\":0}]}\n\ndata: {\"candidates\":[{\"content\":{\"role\":\"model\",\"parts\":[{\"text\":\"流式返回示例。\"}]},\"finishReason\":\"STOP\",\"index\":0}],\"usageMetadata\":{\"totalTokenCount\":27}}"""
        return fenced("http", "HTTP/1.1 200 OK\nContent-Type: text/event-stream\n\n" + body)
    if ":countTokens" in entry:
        return http_json({"totalTokens": 42})
    if ":embedContent" in entry:
        return http_json({"embedding": {"values": [0.0182, -0.0711, 0.0043, 0.1128]}})
    if title == "Router fallback → proxy_handler":
        return http_json({
            "id": "chatcmpl_bc_fallback",
            "object": "chat.completion",
            "model": "resolved-upstream-model",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "该未显式注册路径被数据面 fallback 接管并成功转发。"}, "finish_reason": "stop"}]
        }, note if False else "HTTP/1.1 200 OK")

    # Authentication
    if group == "Authentication":
        if "register" in low:
            return http_json({"success": True, "data": {"token": "eyJhbGciOi...example", "user": {"id": 10001, "username": "demo_user", "roles": ["user"]}}})
        if "login" in low:
            return http_json({"success": True, "data": {"token": "eyJhbGciOi...example", "user": {"id": 10001, "username": "demo_user", "roles": ["user"]}}})
        if "forgot-password" in low:
            return http_json({"success": True, "message": "如果该邮箱存在，密码重置说明将被发送。"})
        if "reset-password" in low:
            return http_json({"success": True, "message": "Password reset successfully"})
        if "google" in low:
            return http_json({"success": True, "data": {"url": "https://accounts.google.com/o/oauth2/v2/auth?..."}})
        if "github" in low:
            return http_json({"success": True, "data": {"url": "https://github.com/login/oauth/authorize?..."}})

    # Channel Management
    if group == "Channel Management":
        channel = {"id": 12, "name": "openai-primary", "channel_type": "openai", "base_url": "https://api.openai.com", "status": 1, "priority": 100, "weight": 100}
        if entry == "GET /console/api/channel":
            return http_json({"success": True, "data": [channel], "total": 1})
        if entry.startswith("POST "):
            return http_json({"success": True, "data": channel}, "HTTP/1.1 201 Created")
        if entry.startswith("PUT "):
            updated = dict(channel); updated["weight"] = 120
            return http_json({"success": True, "data": updated})
        if entry.startswith("GET "):
            return http_json({"success": True, "data": channel})
        if entry.startswith("DELETE "):
            return http_json({"success": True, "message": "Channel deleted"})

    # Token
    if group == "Token":
        token = {"token": "bc_live_7d4e...example", "user_id": 10001, "name": "production", "status": 1, "quota": 100000000, "ip_whitelist": ["203.0.113.10"]}
        if entry == "GET /console/api/tokens":
            return http_json({"success": True, "data": [token]})
        if entry == "POST /console/api/tokens":
            return http_json({"success": True, "data": token}, "HTTP/1.1 201 Created")
        if entry.endswith("/rotate"):
            return http_json({"success": True, "data": {"new_token": "bc_live_9af2...example", "old_token_valid_until": "2026-08-11T15:30:00+08:00"}})
        if entry.endswith("/revoke-old"):
            return http_json({"success": True, "message": "Old key revoked"})
        if entry.endswith("/ip-whitelist"):
            return http_json({"success": True, "data": {"ip_whitelist": ["203.0.113.10", "203.0.113.11"]}})
        if entry.startswith("GET "):
            return http_json({"success": True, "data": token})
        if entry.startswith("PUT "):
            changed = dict(token); changed["status"] = 0
            return http_json({"success": True, "data": changed})
        if entry.startswith("DELETE "):
            return http_json({"success": True, "message": "Token deleted"})

    # User
    if group == "User":
        if "register" in low:
            return http_json({"success": True, "data": {"id": 10001, "username": "demo_user", "roles": ["user"]}})
        if "login" in low:
            return http_json({"success": True, "data": {"token": "eyJhbGciOi...example", "username": "demo_user"}})
        if "topup" in low:
            return http_json({"success": True, "data": {"user_id": 10001, "amount": 100.0, "currency": "USD", "balance": 286.42}})
        if "check_username" in low:
            return http_json({"success": True, "data": {"username": "demo_user", "available": False}})
        if "recharges" in low:
            return http_json({"success": True, "data": [{"id": 9001, "amount": 100.0, "currency": "USD", "created_at": "2026-08-11T14:30:00+08:00"}]})
        if "list_users" in low:
            return http_json({"success": True, "data": [{"id": 10001, "username": "demo_user", "roles": ["user"], "balance": 286.42}]})

    # Billing / Usage and Logs
    if group == "Billing / Usage":
        if "usage/models" in low:
            return http_json({"period": "month", "models": [{"model": "gpt-5.4", "requests": 8021, "total_tokens": 16600420, "cost": 81.24}]})
        if "/usage/" in low:
            return http_json({"user_id": 10001, "prompt_tokens": 18420560, "completion_tokens": 6912840, "total_tokens": 25333400})
        if "/api/v1/usage" in low:
            return http_json({"period": "month", "requests": 12842, "total_tokens": 25333400, "cost": 126.67})
        return http_json({"user_id": 10001, "currency": "USD", "request_count": 12842, "prompt_tokens": 18420560, "completion_tokens": 6912840, "total_tokens": 25333400, "total_cost": 126.67})
    if group == "Logs":
        if "/usage/" in low:
            return http_json({"user_id": 10001, "prompt_tokens": 18420560, "completion_tokens": 6912840, "total_tokens": 25333400})
        return http_json({"success": True, "data": [{"id": 50123, "user_id": 10001, "model": "gpt-5.4", "channel_id": 12, "status": 200, "prompt_tokens": 28, "completion_tokens": 16, "cost": 0.00042, "created_at": "2026-08-11T14:40:15+08:00"}], "page": 1, "page_size": 20})

    # Monitoring / Security
    if group == "Monitoring / Security":
        if entry == "GET /console/api/monitor":
            return http_json({"cpu_usage": 31.7, "memory_usage": 62.4, "disk_usage": 48.9, "uptime_seconds": 483920})
        if entry.endswith("/events"):
            return http_json({"data": [{"id": "risk_50123", "type": "upstream_error", "severity": "medium", "status": 502, "source": "203.0.113.20", "created_at": "2026-08-11T14:42:31+08:00"}], "total": 1})
        if entry.endswith("/filters") and entry.startswith("GET"):
            return http_json({"enabled": True, "block_4xx_burst": True, "block_5xx_burst": True, "threshold": 20})
        if entry.endswith("/filters") and entry.startswith("PUT"):
            return http_json({"success": True, "data": {"enabled": True, "block_4xx_burst": True, "block_5xx_burst": True, "threshold": 25}})
        if entry.endswith("emergency-circuit-break"):
            return http_json({"success": True, "message": "All known upstream circuits tripped", "reason": "manual emergency isolation"})
        if entry.endswith("circuit-breaker-status"):
            return http_json({"status": "ok", "circuit_breaker": {"open": 2, "half_open": 0, "closed": 17}})
        return http_json({"score": 96, "blocked_count": 14, "threat_sources": 3, "error_rate": 0.012, "sparkline_7d": [98, 97, 97, 96, 96, 95, 96]})

    # Cache
    if group == "Cache":
        if entry.endswith("/stats"):
            return http_json({"enabled": True, "backend": "redis", "hits": 182304, "misses": 21044, "hit_rate": 0.8965, "keys": 3812})
        return http_json({"success": True, "message": "Cache cleared"})

    # Admin / Internal
    if group == "Admin / Internal":
        if entry == "GET /health":
            return http_text("ok")
        if "protected 404" in title:
            return http_json({"error": "API endpoint not found"}, "HTTP/1.1 404 Not Found")
        if entry.endswith("/health"):
            return http_json({"status": "ok", "scheduler": {"policy": "weighted"}, "circuit_breaker": {"open": 0, "closed": 19}, "channels": {"healthy": 19, "degraded": 1}, "rate_budget": {"enabled": True}})
        if entry.endswith("/prices/sync"):
            return http_json({"success": True, "updated_models": 46, "duration_ms": 842})
        if entry.endswith("/trip-all"):
            return http_json({"success": True, "tripped": 19})
        if entry.endswith("/metrics"):
            return http_json({"requests_total": 3482211, "requests_inflight": 37, "upstream_failures_total": 14203, "rate_limited_total": 8231, "channels_healthy": 19})

    # OpenAPI / Swagger
    if group == "OpenAPI / Swagger":
        if "openapi.json" in low:
            return http_json({"openapi": "3.0.3", "info": {"title": "BurnCloud API", "version": "1.0.0"}, "paths": {"/api/auth/login": {"post": {"summary": "Login"}}, "/console/api/channel": {"get": {"summary": "List channels"}}}})
        html = "<!doctype html>\n<html>\n  <head><title>BurnCloud Swagger UI</title></head>\n  <body><div id=\"swagger-ui\"></div></body>\n</html>"
        return http_text(html, content_type="text/html; charset=utf-8")

    # Web UI / LiveView / WebSocket
    if group == "Web UI / LiveView / WebSocket":
        if entry == "GET /ws":
            return fenced("http", "HTTP/1.1 101 Switching Protocols\nUpgrade: websocket\nConnection: Upgrade\nSec-WebSocket-Accept: <computed-value>\n\n# 随后进入双向 WebSocket / LiveView 消息通道")
        if entry == "GET /favicon.ico":
            return fenced("http", "HTTP/1.1 200 OK\nContent-Type: image/x-icon\nContent-Length: 5430\n\n<binary favicon bytes>")
        html = "<!doctype html>\n<html lang=\"zh-CN\">\n  <head><meta charset=\"utf-8\"><title>BurnCloud</title></head>\n  <body><div id=\"main\">Dioxus LiveView shell</div></body>\n</html>"
        return http_text(html, content_type="text/html; charset=utf-8")

    return http_json({"success": True, "message": "Request completed", "entry": entry})


def cli_example(p):
    entry = p["entry"]
    low = entry.lower()
    title = p["title"]

    if entry == "burncloud":
        return fenced("text", "BurnCloud starting...\nmode=server+liveview\ndatabase=ready\nrouter=ready\nlistening=http://0.0.0.0:3000")
    if entry == "burncloud server":
        return fenced("text", "BurnCloud server starting...\ndatabase=ready\nrouter=ready\nhttp=0.0.0.0:3000\nstatus=running")
    if entry == "burncloud router":
        return fenced("text", "BurnCloud router initialized\nchannels=19\nprice_cache=ready\nrate_budget=enabled\nstatus=running")
    if entry == "burncloud client":
        return fenced("text", "BurnCloud client starting...\nui=ready\nstatus=running")

    if " --check-only" in low:
        return fenced("text", "$ " + entry + "\nCurrent version: 1.8.0\nLatest version: 1.8.0\nAlready up to date.")
    if "install --list" in low:
        return fenced("text", "$ " + entry + "\nAvailable software:\n  aria2\n  redis\n  sqlite\n  node")
    if "install --status" in low:
        return fenced("text", "$ " + entry + "\nredis     installed\naria2     installed\nnode      installed")
    if low.startswith("burncloud install"):
        return fenced("text", "$ " + entry + "\nResolving package...\nInstalling...\nVerification: OK\nResult: installed")
    if "bundle create" in low:
        return fenced("text", "$ " + entry + "\nBundle created successfully\nmanifest=OK\noutput=./bundle")
    if "bundle verify" in low:
        return fenced("text", "$ " + entry + "\nManifest: OK\nChecksums: OK\nBundle verification passed")

    if " channel " in low:
        if low.endswith(" list"):
            return fenced("text", "$ " + entry + "\nID   NAME             TYPE     STATUS   PRIORITY\n12   openai-primary   openai   enabled  100\n18   claude-primary   anthropic enabled 90")
        if " show " in low:
            return fenced("text", "$ " + entry + "\nid: 12\nname: openai-primary\ntype: openai\nstatus: enabled\npriority: 100")
        if " delete " in low:
            return fenced("text", "$ " + entry + "\nChannel deleted successfully")
        if " update " in low:
            return fenced("text", "$ " + entry + "\nChannel updated successfully\nid=12\nstatus=enabled")
        return fenced("text", "$ " + entry + "\nChannel created successfully\nid=12")

    if " price " in low:
        if low.endswith(" list") or " show " in low or " get " in low:
            return fenced("text", "$ " + entry + "\nMODEL              INPUT / 1M   OUTPUT / 1M   CURRENCY\ngpt-5.4            2.5000       15.0000       USD\nclaude-sonnet-4-5  3.0000       15.0000       USD")
        if "sync-status" in low:
            return fenced("text", "$ " + entry + "\nlast_sync=2026-08-11T14:45:00+08:00\nmodels=46\nstatus=healthy")
        if " validate " in low:
            return fenced("text", "$ " + entry + "\nSchema: OK\nModels: 46\nErrors: 0\nValidation passed")
        if " export " in low:
            return fenced("text", "$ " + entry + "\nExported 46 model prices\nresult=success")
        if " import " in low:
            return fenced("text", "$ " + entry + "\nImported 46 model prices\nskipped=0\nresult=success")
        if low.endswith(" sync"):
            return fenced("text", "$ " + entry + "\nPrice sync started\nupdated=46\nstatus=success")
        if " delete " in low:
            return fenced("text", "$ " + entry + "\nPrice deleted successfully")
        return fenced("text", "$ " + entry + "\nPrice saved successfully")

    if " tiered " in low:
        if "list-tiers" in low or "check-tiered" in low:
            return fenced("text", "$ " + entry + "\nMODEL: gpt-5.4\n0 - 10M tokens      rate=1.00\n10M - 100M tokens  rate=0.95\n100M+ tokens        rate=0.90")
        if "import-tiered" in low:
            return fenced("text", "$ " + entry + "\nImported tiered pricing rules\nmodels=12\nstatus=success")
        if "delete-tiers" in low:
            return fenced("text", "$ " + entry + "\nTiered pricing rules deleted")
        return fenced("text", "$ " + entry + "\nTier added successfully")

    if " token " in low:
        if low.endswith(" list"):
            return fenced("text", "$ " + entry + "\nNAME        TOKEN                    STATUS   QUOTA\nproduction  bc_live_7d4e...example  enabled  100000000")
        if low.endswith(" create"):
            return fenced("text", "$ " + entry + "\nToken created\nkey=bc_live_7d4e...example")
        if " delete " in low:
            return fenced("text", "$ " + entry + "\nToken deleted successfully")
        return fenced("text", "$ " + entry + "\nToken updated successfully")

    if " protocol " in low:
        if low.endswith(" list"):
            return fenced("text", "$ " + entry + "\nID  NAME       TYPE       ENABLED\n1   OpenAI     openai     yes\n2   Anthropic  anthropic  yes\n3   Gemini     gemini     yes")
        if " show " in low:
            return fenced("text", "$ " + entry + "\nid=1\nname=OpenAI\ntype=openai\nenabled=true")
        if " test " in low:
            return fenced("text", "$ " + entry + "\nConnecting channel... OK\nProtocol handshake... OK\nTest request... 200 OK\nResult: passed")
        if " delete " in low:
            return fenced("text", "$ " + entry + "\nProtocol deleted successfully")
        return fenced("text", "$ " + entry + "\nProtocol saved successfully")

    if " currency " in low:
        if "list-rates" in low:
            return fenced("text", "$ " + entry + "\nUSD/CNY  7.18\nEUR/USD  1.09\nupdated_at=2026-08-11T14:40:00+08:00")
        if "convert" in low:
            return fenced("text", "$ " + entry + "\n100.00 USD = 718.00 CNY")
        if "refresh" in low:
            return fenced("text", "$ " + entry + "\nExchange rates refreshed\nupdated=8\nstatus=success")
        return fenced("text", "$ " + entry + "\nExchange rate saved successfully")

    if " user " in low:
        if low.endswith(" login"):
            return fenced("text", "$ " + entry + "\nLogin successful\nusername=demo_user\nclient state saved")
        if low.endswith(" register"):
            return fenced("text", "$ " + entry + "\nUser created\nid=10001\nusername=demo_user")
        if low.endswith(" list"):
            return fenced("text", "$ " + entry + "\nID     USERNAME    ROLES   BALANCE\n10001  demo_user   user    286.42 USD")
        if "topup" in low:
            return fenced("text", "$ " + entry + "\nTop-up successful\nnew_balance=286.42 USD")
        if "recharges" in low:
            return fenced("text", "$ " + entry + "\nID    AMOUNT      CREATED_AT\n9001  100.00 USD  2026-08-11 14:30:00")
        return fenced("text", "$ " + entry + "\nusername=demo_user\navailable=false")

    if " log " in low:
        if low.endswith(" usage"):
            return fenced("text", "$ " + entry + "\nrequests=12842\nprompt_tokens=18420560\ncompletion_tokens=6912840\ntotal_tokens=25333400")
        return fenced("text", "$ " + entry + "\n2026-08-11 14:40:15  user=10001 model=gpt-5.4 channel=12 status=200 tokens=44 cost=0.00042")

    if " monitor " in low:
        if low.endswith(" status"):
            return fenced("text", "$ " + entry + "\ncpu=31.7%\nmemory=62.4%\ndisk=48.9%\nrouter=healthy")
        return fenced("text", "$ " + entry + "\nMonitor server started\nstatus=running")

    return fenced("text", "$ " + entry + "\nOperation completed successfully")


def binary_example(p):
    name = p["entry"]
    if name == "burncloud-client":
        body = "BurnCloud Client\nui=initialized\nroute=/\nstatus=running"
    elif name == "screenshot_gen":
        body = "VirtualDom rendered\noutput=screenshot.html\nstatus=success"
    elif name == "burncloud-download":
        body = "Download manager initialized\nactive_downloads=1\nstatus=running"
    elif name == "burncloud-loop":
        body = "burncloud-loop\nsubcommands: jobs-aesthetic | css-optimize | gate | gates | list-gates"
    elif name == "client-tray":
        body = "BurnCloud tray initialized\nplatform=windows\nstatus=running"
    else:
        body = f"{name} initialized\nstatus=running"
    return fenced("text", body)


def background_example(p):
    title = p["title"]
    samples = {
        "System Monitor Auto Update": "2026-08-11T14:45:10+08:00 monitor_update cpu=31.7% memory=62.4% disk=48.9% status=ok",
        "Price Sync": "2026-08-11T14:45:11+08:00 price_sync updated_models=46 duration_ms=842 status=success",
        "Exchange Rate Sync": "2026-08-11T14:45:12+08:00 exchange_rate_sync currencies=8 stale=false status=success",
        "AIMD Budget Feedback": "2026-08-11T14:45:13+08:00 aimd channel_id=12 result=success old_budget=96 new_budget=100",
        "Async Router Log Writer": "2026-08-11T14:45:14+08:00 router_log_writer persisted=64 queue_remaining=0 status=ok",
        "Async Request Log Writer": "2026-08-11T14:45:15+08:00 request_log_writer persisted=64 queue_remaining=0 status=ok",
        "Token accessed_time update": "token=bc_live_7d4e...example accessed_time=2026-08-11T14:45:16+08:00 update=success",
        "Quota deduction": "user_id=10001 cost=0.00042 quota_before=100.00000 quota_after=99.99958 status=success",
        "Video task mapping save": "task_id=video_task_bc_01JXYZ channel_id=12 user_id=10001 mapping_saved=true",
        "API version detect / update": "channel_id=12 detected_api_version=v1 version_cache_updated=true",
        "Download progress monitor": "gid=2089b05ecca3d829 progress=64.8% speed=42.1MB/s status=active",
        "Restore incomplete downloads": "restored_downloads=3 monitors_restarted=3 status=success",
        "Windows tray thread": "tray=started icon=visible menu_items=3 status=running",
        "Show-window poll loop": "show_window=true visible=true focused=true poll_interval_ms=100",
    }
    return fenced("text", samples.get(title, f"job={title}\nstatus=success"))


def startup_example(p):
    title = p["title"]
    if title == "src/main.rs":
        body = "dotenv=loaded\nmaster_key=ready\nlogging=initialized\nmode=server+liveview\nstartup_dispatch=success"
    elif title == "start_server":
        body = "database=connected\nrouter_db=initialized\nuser_db=initialized\nlistener=0.0.0.0:3000\nserver=running"
    elif title == "create_app":
        body = "monitor=started\ncache=ready\nmanagement_routes=mounted\ninternal_routes=mounted\nliveview=enabled\ndata_plane_fallback=mounted"
    elif title == "create_router_app":
        body = "http_client=ready\nmodel_router=ready\ncircuit_breaker=ready\nprice_cache=ready\nexchange_rates=ready\nbackground_writers=running\nrouter=ready"
    else:
        body = f"startup={title}\nstatus=ready"
    return fenced("text", body)


def ui_example(p):
    group = p["group"]
    entry = p["entry"]
    title = p["title"]

    if group == "Local UI State":
        states = {
            "i18n context": '{\n  "locale": "zh-CN",\n  "fallback_locale": "en-US",\n  "ready": true\n}',
            "Toast state / ToastContainer": '{\n  "visible": true,\n  "level": "success",\n  "message": "操作成功"\n}',
            "Auth context": '{\n  "authenticated": true,\n  "user_id": 10001,\n  "username": "demo_user"\n}',
            "Theme state": '{\n  "theme": "system",\n  "resolved": "dark"\n}',
        }
        return fenced("json", states.get(title, '{"ready": true}'))

    if group == "Desktop UI":
        if title == "window maximize":
            body = "window.maximized=true\nwindow.visible=true"
        elif title == "Windows tray startup":
            body = "tray.visible=true\ntray.status=running"
        else:
            body = "show_window=true\nwindow.visible=true\nwindow.focused=true"
        return fenced("text", body)

    component = entry.strip("/") or "home"
    if "NotFound" in entry:
        body = f"route={entry}\ncomponent=NotFoundPage\nrendered=true"
    else:
        body = f"route={entry}\ncomponent={component}\nrendered=true\nlocale=zh-CN\ntheme=system"
    return fenced("text", body)


def make_example(p):
    section_name = p["section"]
    if section_name == "HTTP / API":
        return section(http_example(p))
    if section_name == "CLI / Executables":
        if p["group"] == "Workspace Binaries":
            return section(binary_example(p), "以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。")
        return section(cli_example(p), "以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。")
    if section_name == "Background Jobs / Async Side Effects":
        return section(background_example(p), "后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。")
    if section_name == "Startup":
        return section(startup_example(p), "Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。")
    if section_name == "UI-only Actions":
        return section(ui_example(p), "UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。")
    return section(fenced("text", "status=success"))


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    updated = 0
    missing = []

    for p in manifest["pages"]:
        path = DOCS / (p["docid"] + ".md")
        if not path.exists():
            missing.append(str(path))
            continue
        text = path.read_text(encoding="utf-8")
        if "## 返回结果示例" in text:
            continue
        if MARKER not in text:
            raise RuntimeError(f"insertion marker not found: {path}")
        text = text.replace(MARKER, make_example(p) + "## 穿过的源码文件\n", 1)
        path.write_text(text, encoding="utf-8")
        updated += 1

    if missing:
        raise RuntimeError("manifest pages missing: " + ", ".join(missing[:10]))

    print(f"Added return-result examples to {updated} generated pages")
    if updated != manifest["page_count"]:
        raise RuntimeError(f"expected to update {manifest['page_count']} pages, got {updated}")


if __name__ == "__main__":
    main()
