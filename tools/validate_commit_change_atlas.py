#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

REQUIRED = [
    "## 1. Change Scope",
    "## 2. User Flow Impact",
    "## 3. End-to-End Runtime Diff",
    "## 4. ICFG Diff",
    "## 5. State Mutation Diff",
    "## 6. API Contract Diff",
    "## 7. Database / Persistence Diff",
    "## 8. External Dependency Diff",
    "## 9. Blast Radius",
    "## 10. Test Coverage & Evidence",
    "## Risk Assessment",
    "## Reviewer Checklist",
    "## Source Diff Entry Points",
]
EVIDENCE_RE = re.compile(r"https://github\.com/burncloud/burncloud/blob/([0-9a-f]{40})/([^\s)#]+)#L(\d+)-L(\d+)")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
NODE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\{)", re.M)

def git(repo: Path, *args: str, check=True):
    p = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode: raise RuntimeError(p.stderr)
    return p.stdout

def parse_frontmatter(text: str):
    m=FM_RE.match(text)
    if not m: return {}
    out={}
    for line in m.group(1).splitlines():
        if ":" not in line: continue
        k,v=line.split(":",1); out[k.strip()]=v.strip().strip('"')
    return out

def lines_at(repo: Path, sha: str, path: str):
    p = subprocess.run(["git","show",f"{sha}:{path}"], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode: return None
    return p.stdout.decode("utf-8","replace").splitlines()

def validate(docs: Path, repo: Path):
    errors=[]; index_path=docs/"commit-index.json"
    if not index_path.exists(): return ["missing docs/commit-index.json"]
    records=json.loads(index_path.read_text(encoding="utf-8"))
    if len(records)!=30: errors.append(f"expected exactly 30 records, got {len(records)}")
    targets=[r.get("target") for r in records]
    if len(set(targets))!=len(targets): errors.append("duplicate target commits in index")
    md_files=sorted((docs/"commits").glob("*.md"))
    if len(md_files)!=30: errors.append(f"expected exactly 30 commit Markdown files, got {len(md_files)}")
    json_files=sorted((docs/"commits").glob("*.json"))
    if len(json_files)!=31: errors.append(f"expected 31 JSON files in commits/ including category, got {len(json_files)}")
    evidence_checked=0; mermaids=0
    for md in md_files:
        text=md.read_text(encoding="utf-8"); fm=parse_frontmatter(text)
        for k in ["doc_type","repository","pr_number","base_commit","target_commit","risk","merged_at"]:
            if not fm.get(k): errors.append(f"{md.name}: missing frontmatter {k}")
        if fm.get("doc_type")!="commit-change-atlas": errors.append(f"{md.name}: wrong doc_type")
        base=fm.get("base_commit",""); target=fm.get("target_commit","")
        if re.fullmatch(r"[0-9a-f]{40}", target or ""):
            parents=git(repo,"show","-s","--format=%P",target,check=False).strip().split()
            if not parents: errors.append(f"{md.name}: target commit unavailable: {target}")
            elif base!=parents[0]: errors.append(f"{md.name}: base {base} is not first parent {parents[0]} of target {target}")
        else: errors.append(f"{md.name}: invalid target commit")
        for heading in REQUIRED:
            n=text.count(heading)
            if n!=1: errors.append(f"{md.name}: heading {heading!r} count={n}, expected 1")
        if "AUTHOR-STATED INTENT" not in text and "⚠ INFERRED INTENT" not in text: errors.append(f"{md.name}: intent truth not marked")
        if "blob/main/" in text: errors.append(f"{md.name}: commit evidence must never bind to main")
        for i in range(1,11):
            if f"| {i}." not in text: errors.append(f"{md.name}: dashboard missing dimension {i}")
        blocks=re.findall(r"```mermaid\n(.*?)```",text,re.S); mermaids += len(blocks)
        for j,b in enumerate(blocks,1):
            nodes=set(NODE_RE.findall(b))
            if len(nodes)>30: errors.append(f"{md.name}: Mermaid #{j} has {len(nodes)} nodes > 30")
            if not re.search(r"\b(flowchart|sequenceDiagram|stateDiagram|graph)\b",b): errors.append(f"{md.name}: Mermaid #{j} missing supported diagram header")
        for sha,path,a,b in EVIDENCE_RE.findall(text):
            evidence_checked+=1; a=int(a); b=int(b); lines=lines_at(repo,sha,path.replace("%20"," "))
            if lines is None: errors.append(f"{md.name}: missing historical evidence file {sha}:{path}"); continue
            if not (1<=a<=b<=len(lines)): errors.append(f"{md.name}: bad evidence range {sha}:{path}:L{a}-L{b}; file has {len(lines)} lines")
        if "### Evidence" not in text: errors.append(f"{md.name}: no Evidence sections")
        if "COMPLETE DIFF SCAN" not in text and not EVIDENCE_RE.search(text): errors.append(f"{md.name}: no source evidence or complete-diff absence basis")
    if evidence_checked < 30: errors.append(f"too few historical evidence links checked: {evidence_checked}")
    print(f"Commit docs: {len(md_files)}"); print(f"Mermaid diagrams: {mermaids}"); print(f"Historical evidence links checked: {evidence_checked}")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("docs",type=Path); ap.add_argument("source_repo",type=Path); a=ap.parse_args(); errors=validate(a.docs.resolve(),a.source_repo.resolve())
    if errors:
        print("ERRORS:"); [print("-",e) for e in errors]; sys.exit(1)
    print("OK: strict 30-commit / 10-dimension Change Atlas validation passed")
if __name__=="__main__": main()
