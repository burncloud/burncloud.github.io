from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'content'; SIDE=(ROOT/'site'/'sidebars.js').read_text(encoding='utf-8'); errors=[]; mds=list(DOCS.rglob('*.md'))
slugmap={}; docids=set()
for p in mds:
 rel=p.relative_to(DOCS).with_suffix('').as_posix(); docids.add(rel); t=p.read_text(encoding='utf-8'); m=re.search(r'^slug:\s*(\S+)',t,re.M)
 if m:
  slug=m.group(1)
  if slug in slugmap and slugmap[slug]!=p: errors.append(f'duplicate slug {slug}')
  slugmap[slug]=p
quoted=set(re.findall(r"['\"]([^'\"]+)['\"]",SIDE)); refs=quoted&docids; explicit=set(re.findall(r"id:\s*['\"]([^'\"]+)['\"]",SIDE))
for ref in sorted(explicit):
 if ref not in docids: errors.append(f'missing sidebar doc: {ref}')
for orphan in sorted(docids-refs): errors.append(f'orphan page not present in sidebar: {orphan}')
for p in mds:
 t=p.read_text(encoding='utf-8'); blocks=re.findall(r'```mermaid\n(.*?)```',t,re.S)
 for block in blocks:
  if 'flowchart' in block:
   nodes=set(re.findall(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\{)',block,re.M))
   if len(nodes)>30: errors.append(f'oversized mermaid ({len(nodes)} nodes): {p.relative_to(DOCS)}')
  for target in re.findall(r'click\s+\w+\s+"([^"]+)"',block):
   if target.startswith('/') and target not in slugmap: errors.append(f'broken mermaid click {target}: {p.relative_to(DOCS)}')
 for target in re.findall(r'\]\((/[^)#?]+/?)(?:#[^)]+)?\)',t):
  if target not in slugmap: errors.append(f'broken markdown link {target}: {p.relative_to(DOCS)}')
 if 'type: runtime-flow' in t and p.relative_to(DOCS).as_posix()!='index.md' and '## Source Evidence' not in t: errors.append(f'missing Source Evidence: {p.relative_to(DOCS)}')
 if ('DynamicAdaptorFactory' in t or 'get_adaptor(' in t) and 'Dynamic' not in t: errors.append(f'unmarked dynamic dispatch: {p.relative_to(DOCS)}')
print(f'Markdown pages: {len(mds)}'); print(f'Mermaid diagrams: {sum(x.read_text(encoding="utf-8").count("```mermaid") for x in mds)}'); print(f'Sidebar doc refs: {len(refs)}')
if errors:
 print('ERRORS:'); [print('-',e) for e in errors]; sys.exit(1)
print('OK: strict User Flow / ICFG consistency checks passed')
