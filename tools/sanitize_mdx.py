from pathlib import Path
import re

from generate_product_docs import build_sidebar, copy_manual_docs

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SIDEBAR = ROOT / "site" / "sidebars.js"

INLINE_CODE = re.compile(r"(`[^`]*`)")


def escape_text(fragment: str) -> str:
    # Generated docs deliberately use literal CLI placeholders such as <model>
    # and route placeholders such as {*path}. Outside code spans/fences MDX
    # interprets those as JSX / expressions, so encode them as HTML entities.
    return (
        fragment
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
    )


def sanitize_inline_content(line: str) -> str:
    # Preserve Markdown syntax that must remain structural. In particular,
    # generated Chinese explanations use blockquotes beginning with `>`.
    prefix = ""
    body = line
    if body.startswith("> "):
        prefix, body = "> ", body[2:]
    elif body.startswith(">"):
        prefix, body = ">", body[1:]

    parts = INLINE_CODE.split(body)
    for idx in range(0, len(parts), 2):
        parts[idx] = escape_text(parts[idx])
    return prefix + "".join(parts)


def sanitize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    in_frontmatter = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if i == 0 and stripped == "---":
            in_frontmatter = True
            out.append(line)
            continue
        if in_frontmatter:
            out.append(line)
            if stripped == "---":
                in_frontmatter = False
            continue

        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        out.append(sanitize_inline_content(line))

    new = "".join(out)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def ensure_node_implementation_plan_sidebar() -> None:
    """Keep the curated Node implementation plan visible after generated sidebar rebuilds."""
    text = SIDEBAR.read_text(encoding="utf-8")
    entry = "        {type:'doc', id:'burncloud-node/implementation-plan', label:'实施计划'},\n"
    marker = "        {type:'doc', id:'burncloud-node/local-api-gateway', label:'Local API Gateway'},\n"

    if entry in text:
        return
    if marker not in text:
        raise RuntimeError("BurnCloud Node sidebar marker not found")

    SIDEBAR.write_text(text.replace(marker, entry + marker, 1), encoding="utf-8")


# generate_atlas.py intentionally rebuilds docs/ from source truth and removes
# non-Atlas directories. Restore the curated BurnCloud product docs immediately
# before MDX sanitization so Node/Network docs and their product-first sidebar are
# part of every Docusaurus build instead of depending on stale generated files.
copy_manual_docs()
build_sidebar()
ensure_node_implementation_plan_sidebar()
print("Injected curated BurnCloud product docs before MDX sanitization")

changed = 0
for md in DOCS.rglob("*.md"):
    if sanitize(md):
        changed += 1

print(f"Sanitized {changed} Markdown files for MDX")
