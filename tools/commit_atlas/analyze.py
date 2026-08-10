from __future__ import annotations
import re
from pathlib import Path
from .common import *

SEM=[
(r'peek_first_chunk|stream_peek','在返回客户端前读取首个 Streaming chunk','peek_first_chunk()'),
(r'EmptyResponseCounter|record_empty','按连续空响应阈值判断是否惩罚 Channel','EmptyResponseCounter'),
(r'record_upstream_success','记录上游成功并更新健康/亲和状态','record_upstream_success()'),
(r'record_upstream_failure|record_failure_with_type','记录上游失败并进入健康/熔断处理','record_upstream_failure()'),
(r'affinity_cache\.evict|\.evict\(','驱逐失败 Channel 的会话亲和','affinity_cache.evict()'),
(r'DEFAULT_JWT_SECRET','统一 JWT 签名与验证密钥','DEFAULT_JWT_SECRET'),
(r'json_error_body|application/json','将 HTTP 错误响应标准化为 JSON Contract','JSON error contract'),
(r'/api/auth|/console/api/auth','调整公共认证 API 路由边界','auth routes'),
(r'router_request_logs','启用详细 Router Request Log 持久化','router_request_logs'),
(r'migration|MIGRATIONS','注册或执行数据库迁移','migration registry'),
(r'safe_cut|is_char_boundary','按 UTF-8 字符边界安全截断日志正文','safe_cut()'),
(r'ResponseQuality|SmartCircuitBreaker|ChannelHealthManager|HealthProbeManager','引入智能响应质量与 Channel 健康/熔断能力','health/circuit modules'),
(r'get_count|force_reset|get_all_counts','增强空响应计数器观测/管理能力','EmptyResponseCounter admin'),
(r'xunfei|xfyun','增加讯飞 Channel 类型与模型配置','xunfei channel'),
(r'BCButton|ButtonVariant','统一 Console 按钮组件与交互语义','BCButton'),
(r'AppStyles|liveview_style_tags|DESIGN_SYSTEM_CSS','统一客户端样式注入顺序','AppStyles'),
(r'/preview/|e2e_preview|e2e-preview','增加免登录 E2E Preview 入口','/preview/*'),
(r'loop\.lock|jobs-aesthetic|css-optimize','增加 UI 优化 Agent Loop 与互斥执行控制','burncloud-loops'),
(r'focus-visible|aria-label','增强 Landing Page 键盘/无障碍交互','focus-visible / aria-label'),
]
SEM=[(re.compile(a,re.I),b,c) for a,b,c in SEM]
FLOW=[
(r'\bstream\b|SSE|peek_first_chunk|bytes_stream','API Requests → Chat Completion → Streaming Response','STATIC CONFIRMED'),
(r'failover|circuit|EmptyResponse|channel_state|affinity|record_upstream_failure|\b429\b|TOO_MANY_REQUESTS','API Requests → Chat Completion → Provider Execution → Failure & Retry','STATIC CONFIRMED'),
(r'passthrough|base_url|/v1/chat/completions','API Requests → Chat Completion → Provider Execution → Passthrough','STATIC CONFIRMED'),
(r'billing|usage|quota','API Requests → Chat Completion → Billing / Usage','⚠ INFERRED'),
(r'crates/router/|proxy_logic|upstream','API Requests → Data Plane','⚠ INFERRED'),
(r'client-access','Console → API Token Management','STATIC CONFIRMED'),
(r'client-models|channel_flow|channel_service','Console → Channel / Model Management','STATIC CONFIRMED'),
(r'client-monitor|monitor_flow|security','Console → Monitor / Security','STATIC CONFIRMED'),
(r'client-users|user_flow|recharge|topup','Console → User / Balance Management','STATIC CONFIRMED'),
(r'client-settings','Console → Settings','STATIC CONFIRMED'),
(r'client-playground','Console → Playground','STATIC CONFIRMED'),
(r'login|register|forgot-password|reset-password|auth_flow|/api/auth','Account Access / Authentication','STATIC CONFIRMED'),
(r'/preview/|e2e_preview|e2e-preview','Developer → E2E Preview','STATIC CONFIRMED'),
(r'crates/loops|jobs-aesthetic|css-optimize','Developer → Agent Optimization Loop','STATIC CONFIRMED'),
(r'router_request_logs|request_log','Data Plane → Request Logging / Observability','STATIC CONFIRMED'),
(r'docs/|README\.md','Engineering → Documentation / Agent Context','STATIC CONFIRMED'),
(r'\.github/workflows|check-ui-conventions','Engineering → CI / UI Quality Gate','STATIC CONFIRMED'),
]
FLOW=[(re.compile(a,re.I),b,c) for a,b,c in FLOW]
RISK=[
('Authentication change',5,r'auth|jwt|login|password|credential'),('Authorization change',5,r'authorization|permission|admin|role|claims'),
('Billing change',5,r'billing|cost|price'),('Quota change',5,r'quota'),('Public API contract',5,r'route\(|StatusCode|CONTENT_TYPE|application/json|/api/|/v1/'),
('Database schema',5,r'migration|CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE|CREATE\s+INDEX'),('Routing decision',4,r'route_with_scheduler|get_candidates|candidate|scheduler|priority|affinity'),
('Provider request',4,r'reqwest|provider|adaptor|upstream|base_url|send\(\)\.await'),('Streaming',4,r'stream|SSE|bytes_stream|peek_first_chunk'),
('Retry/failover',4,r'retry|failover|continue|429|TOO_MANY_REQUESTS|UNAUTHORIZED|PAYMENT_REQUIRED'),('State mutation',3,r'record_|update_|insert\(|remove\(|evict\(|reset\('),
('Dynamic dispatch boundary',3,r'dyn\s+|trait\s+|get_adaptor|ChannelType'),('Cache behavior',3,r'cache|affinity')]
RISK=[(a,b,re.compile(c,re.I)) for a,b,c in RISK]

def changed_symbols(repo:Path,files,base,target):
    ans=set()
    for f in files:
        if not f.path.endswith('.rs'): continue
        for sha,p,newside in [(target,f.newp,True),(base,f.oldp,False)]:
            lines=show_lines(repo,sha,p)
            for h in f.hunks:
                start=h.new if newside else h.old; count=h.newn if newside else h.oldn
                if count<=0: continue
                for ln in range(start,start+count):
                    for k in range(min(ln-1,len(lines)-1),max(-1,ln-80),-1):
                        m=DECL.match(lines[k])
                        if m:
                            kind='function' if m.group(1) else m.group(3); name=m.group(2) or m.group(4)
                            ans.add((p,kind,name,k+1)); break
    return sorted(ans)

def signals(text,regex,limit=12): return list(dict.fromkeys(compact(x,120) for x in text.splitlines() if regex.search(x)))[:limit]
def routes(text): return list(dict.fromkeys(compact(m.group(1),120) for m in ROUTE.finditer(text)))[:20]
def semantic_events(text,kind):
    out=[]
    for line in text.splitlines():
        s=line.strip()
        for rx,msg,entity in SEM:
            if rx.search(s): out.append((msg,entity,kind)); break
        else:
            if CONTROL.search(s): out.append(('修改控制条件 / 分支语义',compact(s,70),kind))
        if len(out)>=8: break
    return list(dict.fromkeys(out))
def map_flows(paths,text):
    hay='\n'.join(paths)+'\n'+text; out=[]
    for rx,name,truth in FLOW:
        if rx.search(hay) and name not in [x[0] for x in out]: out.append((name,truth))
    return out[:8] or [('⚠ Unable to map changed code to a user-triggered flow','⚠ INFERRED / UNKNOWN')]
def risk(text,files,tests_changed):
    score=0; drivers=[]
    for name,pts,rx in RISK:
        if rx.search(text): score+=pts; drivers.append((name,pts))
    runtime_changed=any(is_runtime(f.path) for f in files)
    if runtime_changed and not tests_changed: score+=3; drivers.append(('Missing direct changed tests',3))
    if len(files)>=20: score+=3; drivers.append(('Large blast radius',3))
    return score,('HIGH' if score>=10 else 'MEDIUM' if score>=5 else 'LOW'),drivers

def blast(repo:Path,target:str,symbols,paths):
    out=[]
    for p,k,n,ln in symbols[:8]: out.append(('🔴 Depth 0',n,f'{p}:L{ln}'))
    seen={(x[1],x[2]) for x in out}
    for p,k,n,ln in symbols[:5]:
        if len(n)<4: continue
        grep=run(repo,'grep','-n','-F',n,target,'--','*.rs',check=False)
        for row in grep.splitlines()[:20]:
            m=re.match(r'([^:]+):(\d+):(.*)',row)
            if not m or m.group(1)==p: continue
            key=(n,f'{m.group(1)}:L{m.group(2)}')
            if key in seen: continue
            seen.add(key); out.append(('🟡 Depth 1 lexical',n,key[1]))
            if len(out)>=18: return out
    return out or [('⚠ Unknown','No symbol boundary','Unable to compute lexical blast radius')]
