# BurnCloud Runtime & Commit Change Atlas

This GitHub Pages repository is rendered by **Docusaurus** and has two evidence-first views:

1. **Runtime Flow & ICFG Atlas** — user action → runtime execution → ICFG → source evidence.
2. **Commit Change Atlas** — the latest 30 merged changesets, each generated across 10 fixed change dimensions from the merge commit's first-parent BASE → TARGET source diff.

## Source trees

- `content/` — Runtime Flow Markdown.
- `docs/` — generated latest-30 Commit Change Atlas Markdown + machine-readable JSON.
- `site/` — Docusaurus renderer and sidebars.
- `tools/generate_commit_change_atlas.py` — deterministic BASE→TARGET change analyzer.
- `tools/validate_commit_change_atlas.py` — strict 30 × 10 dimension and historical-evidence validator.

Generated commit evidence always binds to immutable historical SHAs; it never uses `blob/main/...` links.
