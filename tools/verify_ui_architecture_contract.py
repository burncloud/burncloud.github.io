from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "site" / "manual-docs" / "burncloud-ui"
ARCH = UI / "architecture"
PLAN = UI / "implementation-plan"
UI_INJECTOR = ROOT / "tools" / "inject_ui_architecture_dependency.py"
NODE_BUILD_HOOK = ROOT / "tools" / "inject_node_human_acceptance.py"

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

# The Docusaurus generation chain must make the parent Architecture Contract
# visible on every implementation page and expose the full Architecture tree in
# the BurnCloud UI menu before the Implementation Plan.
assert UI_INJECTOR.is_file(), UI_INJECTOR
injector = UI_INJECTOR.read_text(encoding="utf-8")
for needle in [
    "UI-ARCHITECTURE-DEPENDENCY: REQUIRED",
    "Mandatory Architecture Dependency（强制）",
    "burncloud-ui/architecture/index",
    "架构规范（必读）",
    "Allowed Paths / Conditional Paths / Forbidden Paths",
    "STOP → Architecture Dependency / Foundation Issue",
]:
    assert needle in injector, (UI_INJECTOR, needle)

for name in sorted(REQUIRED_ARCH_DOCS - {"index.md"}):
    doc_id = "burncloud-ui/architecture/" + name.removesuffix(".md")
    assert doc_id in injector, (UI_INJECTOR, doc_id)

assert NODE_BUILD_HOOK.is_file(), NODE_BUILD_HOOK
node_hook = NODE_BUILD_HOOK.read_text(encoding="utf-8")
assert "from inject_ui_architecture_dependency import main as inject_ui_architecture_dependency" in node_hook
assert "inject_ui_architecture_dependency()" in node_hook

print(f"ui_architecture_docs={len(REQUIRED_ARCH_DOCS)}")
print(f"governed_ui_issues={len(issues)}")
print("ui_architecture_menu=REQUIRED")
print("ui_issue_architecture_dependency=REQUIRED")
print("ui_architecture_contract=OK")
