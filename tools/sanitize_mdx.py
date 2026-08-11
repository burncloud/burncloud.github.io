from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

INLINE_CODE = re.compile(r"(`[^`]*`)")


def escape_text(fragment: str) -> str:
    # Generated docs deliberately use literal CLI placeholders such as <model>
    # and route placeholders such as {*path}. Outside code spans/fences MDX
    # interprets those as JSX / expressions, so encode them as HTML entities.
    # Do not escape ampersands globally: generated prose may already contain
    # entities after a repeated local run.
    return (
        fragment
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
    )


def sanitize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    in_frontmatter = False
    frontmatter_seen = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if i == 0 and stripped == "---":
            in_frontmatter = True
            frontmatter_seen = True
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

        parts = INLINE_CODE.split(line)
        for idx in range(0, len(parts), 2):
            parts[idx] = escape_text(parts[idx])
        out.append("".join(parts))

    new = "".join(out)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


changed = 0
for md in DOCS.rglob("*.md"):
    if sanitize(md):
        changed += 1

print(f"Sanitized {changed} Markdown files for MDX")
