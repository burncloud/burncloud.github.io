# BurnCloud Runtime Flow & ICFG Atlas

This site **must be rendered by Docusaurus**. Documentation is organized only by runtime user execution flow:

`User Action → End-to-End Flow → Drill-down ICFG → smaller ICFG → Source Evidence`

- `content/` — source Markdown.
- `site/` — Docusaurus renderer, Mermaid configuration, and User Flow sidebar.
- `tools/` — strict consistency and Evidence validators.
- GitHub Actions validates against `burncloud/burncloud@main`, builds Docusaurus, then publishes the generated build to `main:/` for the existing GitHub Pages configuration.
