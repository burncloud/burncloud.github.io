from __future__ import annotations

import argparse
import re
from pathlib import Path
from .common import merged_prs
from .render import render, write_index

_DISPLAY_TRANS = str.maketrans({
    '{': '｛', '}': '｝', '<': '‹', '>': '›', '[': '［', ']': '］',
    '(': '（', ')': '）', '|': '¦', '`': '′', '\\': '＼',
    '*': '＊', '_': '＿', '#': '＃', '~': '～', '!': '！',
})


def safe_author_text(value: str | None, limit: int) -> str:
    """Create a display-only copy of author text that MDX cannot execute.

    The semantic analyzer still receives the same words and intent. Only syntax-like
    punctuation is made inert, whitespace is flattened, and long PR bodies are shortened
    so a beginner-facing page is not buried under the original PR description.
    """
    s = re.sub(r'\s+', ' ', value or '').strip()
    s = s.replace('https://', 'https∶／／').replace('http://', 'http∶／／')
    s = s.translate(_DISPLAY_TRANS)
    if len(s) > limit:
        s = s[:limit].rstrip() + '……（原 PR 里还有更多说明）'
    return s


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source_repo', type=Path)
    p.add_argument('docs_root', type=Path)
    p.add_argument('--limit', type=int, default=30)
    a = p.parse_args()

    repo = a.source_repo.resolve()
    root = a.docs_root.resolve()
    commits = root / 'commits'
    commits.mkdir(parents=True, exist_ok=True)

    for x in commits.iterdir():
        if x.is_file():
            x.unlink()
    for x in [root / 'index.md', root / 'commit-index.json']:
        if x.exists():
            x.unlink()

    recs = []
    for i, pr in enumerate(merged_prs(a.limit), 1):
        print(f'[{i}/{a.limit}] PR #{pr["number"]}')

        # Renderer/analyzer receives the same semantic words, but not raw MDX syntax.
        # This preserves author-intent hints while preventing arbitrary PR Markdown/JSX
        # from becoming executable Docusaurus MDX on the generated page.
        view_pr = dict(pr)
        view_pr['title'] = safe_author_text(pr.get('title'), 220)
        view_pr['body'] = safe_author_text(pr.get('body'), 320)

        recs.append(render(repo, commits, view_pr, i))

    write_index(root, recs)
    print(f'Generated {len(recs)} Commit Change Atlases')


if __name__ == '__main__':
    main()
