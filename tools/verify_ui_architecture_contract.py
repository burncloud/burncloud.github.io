from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "site" / "manual-docs" / "burncloud-ui"
ARCH = UI / "architecture"
PLAN = UI / "implementation-plan"

REQUIRED_ARCH_DOCS = {
    "index.md",
    "overview.md",
    "directory-contract.md",
    "dependency-rules.md",
    "route-contract.md",
    "authorization-contract.md",
    "api-boundary.md",
    "state-truth-contract.md",
    "shared-component-rules.md",
    "design-system.md",
    "i18n-contract.md",
    "css-contract.md",
    "platform-contract.md",
    "testing-contract.md",
    "code-ownership.md",
    "ai-coding-boundaries.md",
    "architecture-lint.md",
    "migration-plan.md",
}


def frontmatter_title(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    match = re.search(r'^title:\s*["\']?([^"\'\n]+)', text[4:end], re.M)
    return match.group(1).strip() if match else None


missing = sorted(REQUIRED_ARCH_DOCS - {p.name for p in ARCH.glob("*.md")})
assert not missing, f"missing architecture docs: {missing}"

arch_index = (ARCH / "index.md").read_text(encoding="utf-8")
assert "ARCHITECTURE-CONTRACT: REQUIRED" in arch_index
assert "site/manual-docs/burncloud-ui/implementation-plan/ui-*.md" in arch_index

ui_index = (UI / "index.md").read_text(encoding="utf-8")
assert "/burncloud-ui/architecture/" in ui_index
assert "Every UI Implementation Issue" in ui_index

issues = sorted(PLAN.glob("ui-*.md"))
assert len(issues) >= 34, [p.name for p in issues]

for issue in issues:
    text = issue.read_text(encoding="utf-8")
    title = frontmatter_title(text)
    assert title and title.startswith("UI-"), (issue, title)
    assert "slug: /burncloud-ui/implementation-plan/" in text, issue
    assert "UI_ARCHITECTURE_EXEMPT" not in text, issue

# Any document whose frontmatter declares a UI-* implementation unit must live
# inside the governed implementation-plan directory.
for md in UI.rglob("*.md"):
    title = frontmatter_title(md.read_text(encoding="utf-8"))
    if title and title.startswith("UI-"):
        assert md.parent == PLAN, f"UI implementation issue outside governed directory: {md}"

print(f"ui_architecture_docs={len(REQUIRED_ARCH_DOCS)}")
print(f"governed_ui_issues={len(issues)}")
print("ui_architecture_contract=OK")
