from __future__ import annotations
import argparse
from pathlib import Path
from .common import merged_prs
from .render import render,write_index

def main():
    p=argparse.ArgumentParser(); p.add_argument('source_repo',type=Path); p.add_argument('docs_root',type=Path); p.add_argument('--limit',type=int,default=30); a=p.parse_args()
    repo=a.source_repo.resolve(); root=a.docs_root.resolve(); commits=root/'commits'; commits.mkdir(parents=True,exist_ok=True)
    for x in commits.iterdir():
        if x.is_file(): x.unlink()
    for x in [root/'index.md',root/'commit-index.json']:
        if x.exists(): x.unlink()
    recs=[]
    for i,pr in enumerate(merged_prs(a.limit),1):
        print(f'[{i}/{a.limit}] PR #{pr["number"]}'); recs.append(render(repo,commits,pr,i))
    write_index(root,recs); print(f'Generated {len(recs)} Commit Change Atlases')
if __name__=='__main__': main()
