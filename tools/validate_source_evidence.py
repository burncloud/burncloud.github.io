from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'content'; SRC=Path(sys.argv[1]).resolve(); errors=[]; checked=0
pat=re.compile(r'https://github\.com/burncloud/burncloud/blob/main/([^\s)#]+)#L(\d+)(?:-L(\d+))?')
for md in DOCS.rglob('*.md'):
 for path,a,b in pat.findall(md.read_text(encoding='utf-8')):
  checked+=1; f=SRC/path
  if not f.exists(): errors.append(f'missing evidence file {path} referenced by {md.relative_to(DOCS)}'); continue
  n=sum(1 for _ in f.open('r',encoding='utf-8',errors='replace')); a=int(a); b=int(b) if b else a
  if not(1<=a<=b<=n): errors.append(f'invalid line range {path}:L{a}-L{b} (file has {n}) in {md.relative_to(DOCS)}')
print(f'Evidence links checked: {checked}')
if errors: print('ERRORS:'); [print('-',e) for e in errors]; sys.exit(1)
print('OK: every Source Evidence file and line range exists in current BurnCloud source')
