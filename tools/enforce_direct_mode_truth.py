from pathlib import Path
import argparse
import json

import enrich_execution_truth_v4 as v4

DIRECT = {"burncloud", "burncloud server", "burncloud router", "burncloud client"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--manifest", default="docs/atlas-manifest.json")
    args = ap.parse_args()

    src = Path(args.source).resolve()
    mp = Path(args.manifest)
    docs = mp.parent
    manifest = json.loads(mp.read_text(encoding="utf-8"))

    fixed = 0
    for p in manifest["pages"]:
        if p["entry"] not in DIRECT:
            continue
        path = docs / (p["docid"] + ".md")
        text = path.read_text(encoding="utf-8")

        # Re-apply the manually audited branch-specific flow AFTER generic static
        # call expansion. This intentionally removes calls from non-selected
        # match branches (for example the generic Clap CLI path on `server`).
        text, applied = v4.special_direct(p, src, text)
        if not applied:
            raise RuntimeError(f"direct-mode rewrite not applied: {p['entry']}")

        # Keep the negative branch explanation without printing a source path that
        # is not actually traversed. Source-path strings in the graph should mean
        # "executed/traversed", not "explicitly not traversed".
        text = text.replace(
            "│    └─ 此路径不会进入 src/cli/commands.rs",
            "│    └─ 此 direct branch 不进入 Clap CLI dispatch",
        )

        text = text.replace(
            "**Execution classification: STATIC CONFIRMED**",
            "**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE**",
        )
        text = text.replace(
            "**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION**",
            "**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE**",
        )
        path.write_text(text, encoding="utf-8")
        fixed += 1

    if fixed != 4:
        raise RuntimeError(f"expected 4 direct-mode pages, fixed {fixed}")
    print(f"Restored branch-sensitive direct-mode truth on {fixed} pages")


if __name__ == "__main__":
    main()
