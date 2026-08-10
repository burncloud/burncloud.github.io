from __future__ import annotations
import json,re
from pathlib import Path
from .common import *
from .analyze import *

def mermaid(title,before,after,maxn=24):
    b=before[:8]; a=after[:12]
    lines=['```mermaid','flowchart TD',f'  S["{esc(title)}"]']
    prev='S'; idx=0
    for label in b:
        idx+=1; n=f'R{idx}'; lines.append(f'  {n}["🔴 {esc(label)}"]'); lines.append(f'  {prev} --> {n}'); prev=n
    if b and a: lines.append(f'  {prev} --> D{{"Diff"}}'); prev='D'
    for label in a:
        idx+=1; n=f'A{idx}'; lines.append(f'  {n}["🟢 {esc(label)}"]'); lines.append(f'  {prev} --> {n}'); prev=n
    if not b and not a: lines.append('  S --> N["⚪ No changed semantic step detected"]')
    lines+=['```']; return '\n'.join(lines)

def scope_graph(pr,paths,syms,flows):
    areas=[f[0] for f in flows[:5]]
    labels=[f'{len(paths)} changed files',f'{len(syms)} changed symbols']+areas
    return mermaid(f"PR #{pr['number']} Change Scope",[],labels)
def table(before,after,none):
    if not before and not after:return f'**⚪ {none}**'
    rows=['| Before | After |','|---|---|']; n=max(len(before),len(after))
    for i in range(n): rows.append(f"| {'🔴 '+before[i] if i<len(before) else '—'} | {'🟢 '+after[i] if i<len(after) else '—'} |")
    return '\n'.join(rows)
def evidence_md(items,compare,absence):
    if not items:return f'- **COMPLETE DIFF SCAN:** {absence}\n- [Open complete BASE → TARGET diff]({compare})'
    out=[]
    for side,sha,p,a,b in items: out.append(f'- **{side}:** [`{p}:L{a}-L{b}`]({historical_url(sha,p,a,b)})')
    return '\n'.join(out)

def render(repo:Path,out:Path,pr,pos):
    target=pr['merge_commit_sha']; parents=run(repo,'show','-s','--format=%P',target).strip().split()
    if not parents: raise RuntimeError(f'{target} has no parent')
    base=parents[0]; diff=run(repo,'diff',base,target,'--find-renames','--unified=0'); files=parse_patch(diff)
    paths=[f.path for f in files]; status=[]
    ns=run(repo,'diff','--name-status',base,target,'--find-renames').splitlines()
    for row in ns:
        parts=row.split('\t'); status.append((parts[0],parts[-1]))
    plus,minus,alltxt=diff_texts(files); pplus,pminus,prod=diff_texts(files,is_runtime)
    syms=changed_symbols(repo,files,base,target); funcs=[x for x in syms if x[1]=='function']; fl=map_flows(paths,alltxt)
    testpaths=[p for p in paths if is_test(p)]; test_refs=[]
    for p,k,n,ln in syms[:10]:
        g=run(repo,'grep','-n','-F',n,target,'--','*test*.rs','tests/**/*.rs',check=False)
        if g.strip(): test_refs.append((n,g.splitlines()[0]))
    tests='🟢 New Coverage' if testpaths else ('✅ Covered' if test_refs else ('❌ Missing' if any(is_runtime(p) for p in paths) else '? Unable to determine'))
    score,level,drivers=risk(alltxt,files,bool(testpaths))
    runtimechg=bool(pplus.strip() or pminus.strip()); controlchg=bool(CONTROL.search(prod)); statechg=bool(STATE.search(prod)); apichg=bool(HTTP.search(alltxt) or ROUTE.search(alltxt)); dbchg=bool(SQL.search(alltxt) or re.search(r'migration|\.sql', '\n'.join(paths),re.I)); extchg=bool(EXT.search(prod))
    ca,cb=signals(pplus,CONTROL),signals(pminus,CONTROL); sa,sb=signals(pplus,STATE),signals(pminus,STATE); ha,hb=signals(plus,HTTP),signals(minus,HTTP); qa,qb=signals(plus,SQL),signals(minus,SQL); xa,xb=signals(pplus,EXT),signals(pminus,EXT)
    ra,rb=routes(plus),routes(minus); eva,evb=semantic_events(pplus,'ADDED/MODIFIED'),semantic_events(pminus,'REMOVED/OLD')
    compare=compare_url(base,target); all_e=evidence(files,base,target); run_e=evidence(files,base,target,lambda p,b:is_runtime(p)); ctl_e=evidence(files,base,target,lambda p,b:CONTROL.search(b)); st_e=evidence(files,base,target,lambda p,b:STATE.search(b)); api_e=evidence(files,base,target,lambda p,b:HTTP.search(b) or ROUTE.search(b)); db_e=evidence(files,base,target,lambda p,b:SQL.search(b) or p.endswith('.sql') or 'migration' in p); ext_e=evidence(files,base,target,lambda p,b:EXT.search(b)); test_e=evidence(files,base,target,lambda p,b:is_test(p))
    dims=[('Change Scope',True),('User Flow',True),('Runtime',runtimechg),('Control Flow',controlchg),('State',statechg),('API Contract',apichg),('Database',dbchg),('External',extchg),('Blast Radius',True),('Tests',tests!='✅ Covered')]
    dashboard=['| Dimension | Status | Risk |','|---|---|---|']
    for i,(name,ch) in enumerate(dims,1): dashboard.append(f"| {i}. {name} | {'● Changed' if ch else '○ No Change'} | {'HIGH' if ch and level=='HIGH' and name in ['Runtime','Control Flow','API Contract','Database','Tests'] else 'MEDIUM' if ch and level!='LOW' else 'LOW'} |")
    filesmd='\n'.join(f"- {'🟢 ADDED' if s.startswith('A') else '🔴 REMOVED' if s.startswith('D') else '🟡 MODIFIED'} `{p}`" for s,p in status[:25]) or '- No files'
    symsmd='\n'.join(f'- 🟡 `{k}` `{n}` — `{p}:L{ln}`' for p,k,n,ln in syms[:25]) or '- No safe Rust symbol boundary resolved; no symbol is guessed.'
    flowmd='\n'.join(f'- **{n}** — {q}' for n,q in fl)
    br=blast(repo,target,syms,paths); brtable='\n'.join(f'| {d} | {n} | `{loc}` |' for d,n,loc in br)
    intent=pr['title']; slug=f"{pr['merged_at'][:10]}-pr-{pr['number']}-{target[:8]}"
    summary=[('Commit',f'`{target}`'),('Base',f'`{base}`'),('Merged PR',f"[#{pr['number']}]({pr['html_url']})"),('Merged At',f"`{pr['merged_at']}`"),('Intent',intent),('Intent Truth','**AUTHOR-STATED** (PR title/body)'),('Risk',f'**{level} ({score})**'),('Changed Files',str(len(paths))),('Changed Symbols',str(len(syms))),('Changed Functions',str(len(funcs))),('Changed Routes',str(len(set(ra+rb)))),('Changed Test Files',str(len(testpaths))),('Affected User Flows',str(len(fl))),('API Contract','Changed' if apichg else 'No Change'),('Database','Changed' if dbchg else 'No Change'),('External','Changed' if extchg else 'No Change'),('Tests',tests)]
    sm='\n'.join(f'| {a} | {b} |' for a,b in summary); riskmd='\n'.join(f'- `{n}` **+{pts}**' for n,pts in drivers) or '- No configured high-risk driver matched.'
    doc=f'''---\ntitle: "PR #{pr['number']} · {intent.replace('"','\\"')}"\nslug: /commits/{slug}/\nsidebar_position: {pos}\ndoc_type: commit-change-atlas\ntruth: source-diff-derived\nrepository: {REPO}\npr_number: {pr['number']}\nbase_commit: {base}\ntarget_commit: {target}\nrisk: {level}\nmerged_at: {pr['merged_at']}\n---\n\n# Commit Change Atlas\n\n## Executive Summary\n\n| Field | Value |\n|---|---|\n{sm}\n\n**Source Diff:** [BASE `{base[:12]}` → TARGET `{target[:12]}`]({compare})\n\n## Intent\n\n**Intent:** {intent}\n\n**Truth:** **AUTHOR-STATED INTENT** — PR title/body; code facts below come from BASE→TARGET diff.\n\n[Open merged PR #{pr['number']}]({pr['html_url']})\n\n## 10-Dimension Dashboard\n\n{chr(10).join(dashboard)}\n\n---\n\n## 1. Change Scope\n\n### What changed?\n\nFiles **{len(paths)}** · Symbols **{len(syms)}** · Functions **{len(funcs)}** · Routes **{len(set(ra+rb))}** · Test files **{len(testpaths)}**\n\n### Change Scope Map\n\n{scope_graph(pr,paths,syms,fl)}\n\n### Changed Files\n\n{filesmd}\n\n### Changed Symbols\n\n{symsmd}\n\n### Evidence\n\n{evidence_md(all_e,compare,'No changed hunk found.')}\n\n---\n\n## 2. User Flow Impact\n\n### Which user behaviors changed?\n\n{flowmd}\n\n### User Flow Impact Map\n\n{mermaid('User Flow Impact',[],[f'{n} · {q}' for n,q in fl])}\n\nOnly explicit runtime/UI entry evidence is STATIC CONFIRMED; path/module mappings remain `⚠ INFERRED` where applicable.\n\n### Evidence\n\n{evidence_md(run_e or all_e[:5],compare,'No production runtime hunk matched; impact may be test/docs/CI only.')}\n\n---\n\n## 3. End-to-End Runtime Diff\n\n### What changed at runtime?\n\n{'Changed production runtime signals were detected.' if runtimechg else '**⚪ NO PRODUCTION RUNTIME EXECUTION CHANGE DETECTED.**'}\n\n### E2E Diff\n\n{mermaid(fl[0][0],[f'{m} · {e}' for m,e,_ in evb],[f'{m} · {e}' for m,e,_ in eva])}\n\n### Decisions\n\n{'Changed control statements are isolated in Dimension 4.' if controlchg else '⚪ No changed control statement detected.'} Unproven edges are not invented.\n\n### Evidence\n\n{evidence_md(run_e,compare,'No conservative runtime-semantic hunk matched.')}\n\n---\n\n## 4. ICFG Diff\n\n### Which control-flow semantics changed?\n\n{mermaid('Changed Control Region',cb,ca)}\n\n{'⚠ Diagram contains changed control statements only; unproven interprocedural edges are not invented.' if controlchg else '**⚪ NO CONTROL-FLOW CHANGE DETECTED.**'}\n\n### Evidence\n\n{evidence_md(ctl_e,compare,'No if/match/loop/break/continue/return/spawn statement changed.')}\n\n---\n\n## 5. State Mutation Diff\n\n### What state behavior changed?\n\n{table(sb,sa,'NO STATE MUTATION CHANGE DETECTED')}\n\n### State Diff\n\n{mermaid('State Mutation Diff',sb,sa)}\n\n### Evidence\n\n{evidence_md(st_e,compare,'No changed DB/cache/counter/update state signal detected.')}\n\n---\n\n## 6. API Contract Diff\n\n### API changes\n\n{table(hb+rb,ha+ra,'NO API CONTRACT CHANGE DETECTED')}\n\n{'API Contract changes are never rated below MEDIUM.' if apichg else '**API Contract: ⚪ NO CHANGE DETECTED** by complete diff scan.'}\n\n### Evidence\n\n{evidence_md(api_e,compare,'No route/status/header/content-type API-contract marker changed.')}\n\n---\n\n## 7. Database / Persistence Diff\n\n### Persistence changes\n\n{table(qb,qa,'NO DATABASE / PERSISTENCE CHANGE DETECTED')}\n\n{'Database/migration/SQL persistence surface changed.' if dbchg else '**⚪ NO DATABASE / PERSISTENCE CHANGE DETECTED** by complete diff scan.'}\n\n### Evidence\n\n{evidence_md(db_e,compare,'No migration/database/SQL persistence hunk changed.')}\n\n---\n\n## 8. External Dependency Diff\n\n### External behavior changes\n\n{table(xb,xa,'NO EXTERNAL DEPENDENCY CHANGE DETECTED')}\n\n{'**🟣 DYNAMIC:** concrete Provider/Adaptor target remains runtime-dependent.' if DYNAMIC.search(prod) else ''}\n{'**⚪ NO EXTERNAL DEPENDENCY CHANGE DETECTED** by complete diff scan.' if not extchg else ''}\n\n### Evidence\n\n{evidence_md(ext_e,compare,'No outbound HTTP/provider/Redis/webhook/process marker changed.')}\n\n---\n\n## 9. Blast Radius\n\n### What else may be affected?\n\n| Depth | Impact | Evidence location |\n|---|---|---|\n{brtable}\n\n### Blast Radius Map\n\n{mermaid('Blast Radius',[],[f'{d}: {n}' for d,n,_ in br])}\n\n🔴 Depth 0 is direct. 🟡 lexical references are **impact candidates**, not compiler-proven call edges. Dynamic dispatch is never promoted to a confirmed edge.\n\n### Evidence\n\n{evidence_md(all_e[:7],compare,'No changed hunk.')}\n\n---\n\n## 10. Test Coverage & Evidence\n\n### Coverage Matrix\n\n**Overall:** {tests}\n\n- Changed test files: **{len(testpaths)}**\n- Lexical references from changed symbols into tests: **{len(test_refs)}**\n\n### Missing Coverage\n\n{'- ❌ Direct changed-test coverage was not detected for changed production symbols.' if tests=='❌ Missing' else '- No additional missing direct-coverage claim beyond evidence above.'}\n\n### Source Evidence\n\n{evidence_md(test_e,compare,'No changed test hunk; coverage status uses changed tests plus lexical test references.')}\n\n---\n\n## Risk Assessment\n\n**Score: {score} → {level}**\n\n### Risk Drivers\n\n{riskmd}\n\nThe score is rule-based, not an LLM impression.\n\n## Reviewer Checklist\n\n- [ ] Intent 与代码变化一致\n- [ ] User Flow impact 已确认\n- [ ] Runtime Diff 已确认\n- [ ] Control-flow changes 已确认\n- [ ] State mutation 已确认\n- [ ] API contract 已确认\n- [ ] Database behavior 已确认\n- [ ] External Provider behavior 已确认\n- [ ] Blast Radius 可接受\n- [ ] Tests 覆盖 changed runtime paths\n- [ ] Dynamic / Inferred relationships 已正确标记\n- [ ] Source Evidence 可追溯\n\n## Source Diff Entry Points\n\n- [Complete BASE → TARGET diff]({compare})\n- [Merged PR #{pr['number']}]({pr['html_url']})\n'''
    out.mkdir(parents=True,exist_ok=True); md=out/f'{slug}.md'; md.write_text(doc,encoding='utf-8')
    rec={'pr_number':pr['number'],'title':intent,'merged_at':pr['merged_at'],'base':base,'target':target,'risk':level,'risk_score':score,'files_changed':len(paths),'changed_symbols':len(syms),'changed_functions':len(funcs),'flows':[{'name':a,'truth':b} for a,b in fl],'doc':md.name,'dimensions':{n:{'status':'Changed' if c else 'No Change'} for n,c in dims}}
    (out/f'{slug}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8'); return rec

def write_index(root:Path,recs):
    lines=['---','title: "Commit Change Atlas"','slug: /','sidebar_position: 1','doc_type: commit-change-index','---','','# BurnCloud Commit Change Atlas','','最近 **30 个已合并 Pull Request changeset**。每篇以 merge commit 第一父提交为 BASE、merge commit 为 TARGET。','','**原则：** `Diff First → Evidence First → No Guessing`；历史 Evidence 永远绑定不可变 SHA。','','## Latest 30 merged changesets','','| # | Merged | PR | Target | Risk | Files | Symbols |','|---:|---|---|---|---|---:|---:|']
    for i,r in enumerate(recs,1):
        slug=Path(r['doc']).stem; lines.append(f"| {i} | {r['merged_at'][:10]} | [#{r['pr_number']}]({WEB}/pull/{r['pr_number']}) | [`{r['target'][:8]}`](./commits/{slug}.md) | **{r['risk']}** | {r['files_changed']} | {r['changed_symbols']} |")
    lines += ['', '## 10 Change Dimensions','', '1. Change Scope','2. User Flow Impact','3. End-to-End Runtime Diff','4. ICFG Diff','5. State Mutation Diff','6. API Contract Diff','7. Database / Persistence Diff','8. External Dependency Diff','9. Blast Radius','10. Test Coverage & Evidence']
    root.mkdir(parents=True,exist_ok=True); (root/'index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); (root/'commit-index.json').write_text(json.dumps(recs,ensure_ascii=False,indent=2),encoding='utf-8'); (root/'commits'/'_category_.json').write_text(json.dumps({'label':'Latest 30 Merged Changes','position':2,'collapsed':False},indent=2),encoding='utf-8')
