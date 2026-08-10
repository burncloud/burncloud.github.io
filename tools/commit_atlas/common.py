from __future__ import annotations
import html, json, os, re, subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO='burncloud/burncloud'
WEB=f'https://github.com/{REPO}'
CONTROL=re.compile(r'\b(if|else\s+if|match|for|while|loop|return|continue|break|tokio::spawn|spawn\()\b')
SQL=re.compile(r'\b(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE|CREATE\s+(?:UNIQUE\s+)?INDEX|UPSERT)\b',re.I)
HTTP=re.compile(r'StatusCode::[A-Z0-9_]+|CONTENT_TYPE|application/json|Retry-After|Authorization|Bearer|x-api-key|x-goog-api-key|\.route\(')
EXT=re.compile(r'reqwest|\.send\(\)\.await|https?://|base_url|timeout\(|Authorization|Bearer|redis|webhook|Command::new',re.I)
STATE=re.compile(r'record_|update_|insert\(|remove\(|evict\(|reset\(|clear_|store\(|fetch_add|fetch_sub|try_send\(|INSERT\s+INTO|UPDATE\s+|DELETE\s+FROM',re.I)
DYNAMIC=re.compile(r'dyn\s+|get_adaptor|trait\s+|ChannelType|provider_type',re.I)
ROUTE=re.compile(r'[\"\'](/(?:api|console|v1|health|preview)[^\"\']*)[\"\']')
DECL=re.compile(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:(fn)\s+([A-Za-z_][\w]*)|(struct|enum|trait|type|const|static|mod)\s+([A-Za-z_][\w]*))')

def run(repo:Path,*args,check=True):
    p=subprocess.run(['git',*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode: raise RuntimeError(f"git {' '.join(args)}: {p.stderr}")
    return p.stdout

def gh(url:str):
    cmd=['curl','-fsSL','--retry','5','--retry-delay','2','--retry-all-errors','--connect-timeout','15','--max-time','60',
         '-H','Accept: application/vnd.github+json','-H','User-Agent: burncloud-change-atlas','-H','X-GitHub-Api-Version: 2022-11-28']
    tok=os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if tok: cmd += ['-H',f'Authorization: Bearer {tok}']
    cmd.append(url)
    p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(f'GitHub API request failed after verified-TLS retries: {p.stderr}')
    return json.loads(p.stdout)

def merged_prs(n:int):
    d={}
    for page in range(1,6):
        rows=gh(f'https://api.github.com/repos/{REPO}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}')
        for p in rows:
            if p.get('merged_at') and p.get('merge_commit_sha'): d[p['number']]=p
        if len(d)>=n*2: break
    out=sorted(d.values(),key=lambda x:x['merged_at'],reverse=True)
    if len(out)<n: raise RuntimeError(f'only {len(out)} merged PRs available')
    return out[:n]

@dataclass
class Hunk:
    old:int; oldn:int; new:int; newn:int; ctx:str
    minus:list[str]=field(default_factory=list); plus:list[str]=field(default_factory=list)
@dataclass
class FileDiff:
    oldp:str; newp:str; hunks:list[Hunk]=field(default_factory=list)
    @property
    def path(self): return self.newp if self.newp!='/dev/null' else self.oldp

def parse_patch(text:str):
    out=[]; f=None; h=None
    for x in text.splitlines():
        if x.startswith('diff --git '):
            m=re.match(r'diff --git a/(.+) b/(.+)',x); f=FileDiff(m.group(1),m.group(2)); out.append(f); h=None
        elif f and x.startswith('--- '): f.oldp=x[4:][2:] if x[4:].startswith('a/') else x[4:]
        elif f and x.startswith('+++ '): f.newp=x[4:][2:] if x[4:].startswith('b/') else x[4:]
        elif f and x.startswith('@@ '):
            m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\s*(.*)',x)
            if m:
                h=Hunk(int(m.group(1)),int(m.group(2) or 1),int(m.group(3)),int(m.group(4) or 1),m.group(5)); f.hunks.append(h)
        elif h:
            if x.startswith('+') and not x.startswith('+++'): h.plus.append(x[1:])
            elif x.startswith('-') and not x.startswith('---'): h.minus.append(x[1:])
    return out

def is_test(path:str): return bool(re.search(r'(^|/)(tests?|e2e)(/|$)|_test\.rs$|test_.*\.rs$',path,re.I))
def is_runtime(path:str): return path.endswith('.rs') and not is_test(path) and not path.startswith('docs/')
def compact(s:str,n=110):
    s=re.sub(r'\s+',' ',s).strip().replace('"',"'")
    return s if len(s)<=n else s[:n-1]+'…'
def esc(s:str): return html.escape(compact(s),quote=False).replace('<','&lt;').replace('>','&gt;')
def show_lines(repo:Path,sha:str,path:str):
    if path=='/dev/null': return []
    x=run(repo,'show',f'{sha}:{path}',check=False); return x.splitlines() if x else []
def historical_url(sha,path,a,b): return f'{WEB}/blob/{sha}/{path.replace(" ","%20")}#L{a}-L{b}'
def compare_url(base,target): return f'{WEB}/compare/{base}...{target}'

def diff_texts(files,predicate=lambda p:True):
    plus=[]; minus=[]
    for f in files:
        if not predicate(f.path): continue
        for h in f.hunks: plus+=h.plus; minus+=h.minus
    return '\n'.join(plus), '\n'.join(minus), '\n'.join(plus+minus)

def evidence(files,base,target,predicate=lambda p,b:True,limit=8):
    out=[]
    for f in files:
        for h in f.hunks:
            blob='\n'.join(h.plus+h.minus)
            if not predicate(f.path,blob): continue
            if h.newn>0 and f.newp!='/dev/null': out.append(('AFTER',target,f.newp,h.new,max(h.new,h.new+h.newn-1)))
            if h.oldn>0 and f.oldp!='/dev/null': out.append(('BASE',base,f.oldp,h.old,max(h.old,h.old+h.oldn-1)))
            if len(out)>=limit: return out[:limit]
    return out[:limit]
